import copy
import tempfile
import unittest
from pathlib import Path
from cryptography.fernet import InvalidToken
from services.access_control.audit_sink import (PolicyEvaluator, AuditLogger, DataMasker, SanctionsChecker, DataEncryption, GDPRCompliance, PolicyEngine, AuditSink, AccessRequest, Action, AccessLevel)
from datetime import datetime, timezone
from unittest.mock import Mock

POLICY={'resource':'onchain_data.curated_events','rules':[{'principal':'role:analyst','action':'SELECT','columns':['transaction_hash','block_number'],'conditions':['value_usd < 10000']}]}

class SecurityTests(unittest.TestCase):
    def test_explicit_policy_and_failures(self):
        p=PolicyEvaluator([POLICY],{'analyst@company.com':['analyst']})
        req=dict(user='analyst@company.com',resource='onchain_data.curated_events',action='SELECT',columns=['transaction_hash'],context={'value_usd':5000})
        self.assertTrue(p.evaluate_access(**req)['allowed'])
        for changed in [dict(user='unmapped@company.com'),dict(action='DELETE'),dict(columns=['transaction_hash','kyc_data']),dict(context={}),dict(context={'value_usd':10000}),dict(context={'value_usd':float('nan')}),dict(resource='other')]:
            self.assertFalse(p.evaluate_access(**(req|changed))['allowed'])
        self.assertFalse(PolicyEvaluator().evaluate_access(**req)['allowed'])
        self.assertFalse(p.evaluate_access(**(req|{'user':'intruder','context':{'role':'analyst','value_usd':1}}))['allowed'])
        p.load_policy({'resource':'*','rules':[{'principal':'*','action':'*','columns':['transaction_hash'],'effect':'deny'}]})
        self.assertFalse(p.evaluate_access(**req)['allowed'])

    def test_policy_rejects_executable_condition(self):
        p=copy.deepcopy(POLICY);p['rules'][0]['conditions']=['__import__("os").system("true")']
        with self.assertRaises(ValueError):PolicyEvaluator([p])

    def test_masking_recursive_and_no_input_mutation(self):
        record={'email':'a@b.c','phone':'+1555','from_address':'0xabc','nested':[{'api_key':'secret','wallet_address':'public'}]};original=copy.deepcopy(record)
        masked=DataMasker().mask_sensitive_data(record)
        self.assertEqual(record,original);self.assertEqual(masked['email'],'***@***.***');self.assertEqual(masked['phone'],'+*-***-***-****');self.assertEqual(masked['nested'][0]['api_key'],'***');self.assertEqual(masked['from_address'],'0xabc')

    def test_audit_durable_chain_tamper_and_provider_failure(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'audit.db';a=AuditLogger(path)
            e=a.log_access('analyst','table','SELECT','DENIED',{'token':'do-not-store'})
            self.assertEqual(e['metadata']['token'],'***');a.close()
            a=AuditLogger(path);self.assertEqual(len(a.get_audit_trail()),1)
            a.log_access('admin','table','DELETE','SUCCESS');self.assertTrue(a.verify_integrity())
            a.provider=lambda event:(_ for _ in ()).throw(ConnectionError('sink unavailable'))
            with self.assertRaises(ConnectionError):a.log_access('admin','table','SELECT','SUCCESS')
            self.assertEqual(len(a.get_audit_trail()),3)
            with a.connection:a.connection.execute("UPDATE events SET payload='{}' WHERE seq=1")
            self.assertFalse(a.verify_integrity())
            with self.assertRaises(RuntimeError):a.get_audit_trail()
            a.close()

    def test_sanctions_unavailable_and_provenanced_matching(self):
        address='0x'+'a'*40;other='0x'+'b'*40
        self.assertIsNone(SanctionsChecker().check_address(address)['is_sanctioned'])
        self.assertTrue(SanctionsChecker().check_address(address)['blocked'])
        with self.assertRaises(ValueError):SanctionsChecker([address])
        checker=SanctionsChecker([{'address':address,'label':'explicit test fixture'}],'fixture-only','2026-10-13')
        self.assertTrue(checker.check_address(address.upper().replace('0X','0x'))['is_sanctioned'])
        self.assertFalse(checker.check_address(other)['is_sanctioned'])
        with self.assertRaises(ValueError):checker.check_address('not-an-address')

    def test_authenticated_encryption_reload_wrong_key_and_tamper(self):
        key=DataEncryption.generate_key();cipher=DataEncryption(key);token=cipher.encrypt('actual private payload')
        self.assertNotEqual(cipher.encrypt('actual private payload'),token)
        self.assertEqual(DataEncryption(key).decrypt(token),'actual private payload')
        with self.assertRaises(InvalidToken):DataEncryption(DataEncryption.generate_key()).decrypt(token)
        with self.assertRaises(InvalidToken):cipher.decrypt(token[:-5]+'ABCDE')
        with self.assertRaises(ValueError):DataEncryption()

    def test_subject_export_delete_real_store(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'subjects.db';s=GDPRCompliance(path);s.store_user_data('one',{'email':'one@x'});s.store_user_data('two',{'name':'two'});s.close()
            s=GDPRCompliance(path);self.assertEqual(s.export_user_data('one')['data'],{'email':'one@x'})
            self.assertEqual(s.delete_user_data('one')['deleted_records'],1);self.assertIsNone(s.export_user_data('one')['data']);self.assertIsNotNone(s.export_user_data('two')['data']);self.assertEqual(s.delete_user_data('one')['deleted_records'],0);s.close()
        with self.assertRaises(ValueError):GDPRCompliance()

    def test_original_unknown_role_conditions_fail_closed(self):
        engine=object.__new__(PolicyEngine);engine.identities={'known':['unused']}
        self.assertEqual(engine._determine_user_role('admin@company.com',''), 'unknown')
        self.assertEqual(engine._determine_user_role('','fake-ingestion-account'), 'unknown')
        engine.policies={'roles':{'analyst':{'conditions':['unknown_restriction']}}}
        request=AccessRequest('x','','curated_events',Action.READ,{},datetime.now(timezone.utc))
        self.assertFalse(engine._evaluate_conditions('analyst',request,AccessLevel.INTERNAL)[0])

    def test_original_denied_attempt_audited_and_sink_failure_denies(self):
        engine=object.__new__(PolicyEngine);engine.identities={'known':'admin'}
        engine.policies=engine._get_default_policies();engine.logger=Mock();engine._log_audit_event=Mock()
        req=AccessRequest('unknown','','raw_events',Action.READ,{},datetime.now(timezone.utc))
        self.assertFalse(engine.evaluate_access(req).granted);engine._log_audit_event.assert_called_once()
        engine._log_audit_event=Mock(side_effect=ConnectionError('offline provider unavailable'))
        req.user_id='known'
        self.assertFalse(engine.evaluate_access(req).granted)

    def test_bigquery_row_rejection_raises_and_message_nacks(self):
        sink=object.__new__(AuditSink);sink.bigquery_client=Mock();sink.logger=Mock();sink.bigquery_client.insert_rows_json.return_value=[{'errors':'rejected'}]
        with self.assertRaises(RuntimeError):sink._store_audit_event({'event':'x'})
        message=Mock();message.data=b'{"event":"x"}';sink._process_audit_event(message)
        message.nack.assert_called_once();message.ack.assert_not_called()

if __name__=='__main__':unittest.main()
