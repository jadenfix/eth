"""Offline security primitives with explicit policy, storage and provider boundaries.

Identity must already be authenticated by the caller. No role is inferred from
email substrings, and absence of a sanctions source is not a clean result.
"""
import ast
import copy
import hashlib
import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _now():
    return datetime.now(timezone.utc).isoformat()


def _condition(expression, context):
    """Evaluate a single scalar comparison without eval or executable AST nodes."""
    node = ast.parse(expression, mode='eval').body
    if not isinstance(node, ast.Compare) or len(node.ops) != 1 or len(node.comparators) != 1:
        raise ValueError('Only one scalar comparison per condition is supported')
    if not isinstance(node.left, ast.Name) or not isinstance(node.comparators[0], ast.Constant):
        raise ValueError('Conditions must compare a context field to a literal')
    if node.left.id not in context:
        return False
    left, right = context[node.left.id], node.comparators[0].value
    if type(left) not in (str, int, float, bool) or type(right) not in (str, int, float, bool):
        raise ValueError('Conditions require scalar values')
    if isinstance(node.ops[0], ast.Lt): return left < right
    if isinstance(node.ops[0], ast.LtE): return left <= right
    if isinstance(node.ops[0], ast.Gt): return left > right
    if isinstance(node.ops[0], ast.GtE): return left >= right
    if isinstance(node.ops[0], ast.Eq): return left == right
    if isinstance(node.ops[0], ast.NotEq): return left != right
    raise ValueError('Unsupported comparison')


class PolicyEvaluator:
    """Explicit principal/role rules; default deny, all requested columns covered.

    Roles are trusted server-side mappings passed at construction, never values
    supplied in the request context. Deny rules override matching allow rules.
    """
    def __init__(self, policies=None, identities=None):
        self.policies = []
        self.identities = copy.deepcopy(identities or {})
        for policy in policies or []:
            self.load_policy(policy)

    def load_policy(self, policy):
        if not isinstance(policy, dict) or not isinstance(policy.get('resource'), str) or not isinstance(policy.get('rules'), list):
            raise ValueError('Policy requires resource and rules')
        for rule in policy['rules']:
            if not isinstance(rule.get('principal'), str) or not isinstance(rule.get('action'), str):
                raise ValueError('Rule requires principal and action')
            if rule.get('effect', 'allow') not in ('allow', 'deny'):
                raise ValueError('Unknown rule effect')
            for condition in rule.get('conditions', []):
                # Validate syntax now; fields are checked again against request context.
                _condition(condition, {})
        self.policies.append(copy.deepcopy(policy))

    def evaluate_access(self, user, resource, action, columns=None, context=None):
        denied = {'allowed': False, 'reason': 'insufficient_permissions'}
        if not user or not resource or not action or not columns:
            return denied
        roles = set(self.identities.get(user, []))
        covered = set()
        for policy in self.policies:
            if policy['resource'] not in (resource, '*'):
                continue
            for rule in policy['rules']:
                principal = rule['principal']
                if principal not in (user, '*') and not (principal.startswith('role:') and principal[5:] in roles):
                    continue
                if rule['action'].upper() not in (action.upper(), '*'):
                    continue
                try:
                    if not all(_condition(c, context or {}) for c in rule.get('conditions', [])):
                        continue
                except (ValueError, TypeError, SyntaxError):
                    return {'allowed': False, 'reason': 'invalid_policy_condition'}
                selected = set(columns) if '*' in rule.get('columns', []) else set(columns) & set(rule.get('columns', []))
                if selected and rule.get('effect', 'allow') == 'deny':
                    return {'allowed': False, 'reason': 'explicit_deny'}
                covered.update(selected)
        return {'allowed': True, 'reason': 'policy_grant'} if covered == set(columns) else denied


class DataMasker:
    """Mask known PII recursively while retaining public blockchain identifiers.

    This is field-based masking, not a claim of automatic DLP classification.
    The admin role is an authenticated server-side decision, not user input.
    """
    EMAIL_FIELDS = {'email', 'user_email', 'email_address'}
    PHONE_FIELDS = {'phone', 'phone_number', 'telephone'}
    PRIVATE_FIELDS = {'name', 'full_name', 'kyc_data', 'ssn', 'date_of_birth', 'password', 'token', 'api_key', 'secret'}

    def mask_sensitive_data(self, data, user_role='analyst'):
        if user_role == 'admin':
            return copy.deepcopy(data)
        if isinstance(data, list):
            return [self.mask_sensitive_data(x, user_role) for x in data]
        if not isinstance(data, dict):
            return copy.deepcopy(data)
        result = {}
        for key, value in data.items():
            field = key.lower()
            if value is None:
                result[key] = None
            elif field in self.EMAIL_FIELDS:
                result[key] = '***@***.***'
            elif field in self.PHONE_FIELDS:
                result[key] = '+*-***-***-****'
            elif field in self.PRIVATE_FIELDS:
                result[key] = '***'
            else:
                result[key] = self.mask_sensitive_data(value, user_role)
        return result


class AuditLogger:
    """Transactional SQLite audit journal with an integrity hash chain.

    Hash chains detect modification/removal inside the journal, not deletion of
    the whole database or malicious rewrites by a privileged database owner.
    An external trusted anchor is necessary for stronger tamper evidence.
    """
    def __init__(self, path=None, evaluator=None, provider=None):
        self.evaluator = evaluator or PolicyEvaluator()
        self.provider = provider
        self.connection = sqlite3.connect(str(path or os.getenv('AUDIT_DB_PATH', 'audit-events.sqlite3')))
        self.connection.execute('CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, payload TEXT NOT NULL, previous TEXT NOT NULL, digest TEXT NOT NULL)')
        self.connection.commit()
        self.session_id = str(uuid.uuid4())

    def check_column_access(self, user, table, column, context=None):
        return self.evaluator.evaluate_access(user, table, 'SELECT', [column], context)

    def log_access(self, user, resource, action, result, metadata=None):
        if not all(isinstance(x, str) and x for x in [user, resource, action, result]):
            raise ValueError('Audit identity/resource/action/result must be nonempty strings')
        metadata = DataMasker().mask_sensitive_data(metadata or {})
        entry = {'event_id': str(uuid.uuid4()), 'user': user, 'resource': resource, 'action': action, 'result': result, 'timestamp': _now(), 'session_id': self.session_id, 'ip_address': metadata.get('ip_address'), 'metadata': metadata}
        payload = json.dumps(entry, sort_keys=True, separators=(',', ':'), allow_nan=False)
        with self.connection:
            self.connection.execute('BEGIN IMMEDIATE')
            previous = self.connection.execute('SELECT digest FROM events ORDER BY seq DESC LIMIT 1').fetchone()
            previous = previous[0] if previous else ''
            digest = hashlib.sha256((previous + payload).encode()).hexdigest()
            self.connection.execute('INSERT INTO events(payload,previous,digest) VALUES (?,?,?)', (payload, previous, digest))
        if self.provider is not None:
            # Local durability already succeeded; remote failure propagates.
            self.provider(entry)
        return entry

    def verify_integrity(self):
        previous = ''
        for payload, stored_previous, digest in self.connection.execute('SELECT payload,previous,digest FROM events ORDER BY seq'):
            if previous != stored_previous or hashlib.sha256((previous + payload).encode()).hexdigest() != digest:
                return False
            previous = digest
        return True

    def get_audit_trail(self, user=None):
        if not self.verify_integrity():
            raise RuntimeError('Audit integrity check failed')
        rows = [json.loads(x[0]) for x in self.connection.execute('SELECT payload FROM events ORDER BY seq')]
        return [x for x in rows if user is None or x['user'] == user]

    def close(self):
        self.connection.close()


class SanctionsChecker:
    """Evaluate an explicitly supplied list; unavailable source is fail closed.

    No bundled address is treated as a current legal sanctions determination.
    Source, retrieval date and list maintenance are deployment responsibilities.
    """
    def __init__(self, addresses=None, source=None, as_of=None):
        if addresses is not None and (not source or not as_of):
            raise ValueError('Sanctions list requires source and as_of provenance')
        self.addresses = addresses
        self.source = source
        self.as_of = as_of

    def _get_sanctions_list(self):
        if self.addresses is None:
            raise RuntimeError('No sanctions source configured')
        return self.addresses

    def check_address(self, address):
        if not isinstance(address, str) or not re.fullmatch(r'0x[0-9a-fA-F]{40}', address):
            raise ValueError('Expected Ethereum address')
        try:
            entries = self._get_sanctions_list()
        except Exception:
            return {'is_sanctioned': None, 'blocked': True, 'status': 'unavailable', 'sanctions_list': [], 'source': self.source, 'as_of': self.as_of}
        matches = []
        for entry in entries:
            candidate = entry.get('address') if isinstance(entry, dict) else entry
            if not isinstance(candidate, str) or not re.fullmatch(r'0x[0-9a-fA-F]{40}', candidate):
                raise ValueError('Malformed sanctions source entry')
            if candidate.lower() == address.lower():
                matches.append(entry.get('label', self.source) if isinstance(entry, dict) else self.source)
        return {'is_sanctioned': bool(matches), 'blocked': bool(matches), 'status': 'matched' if matches else 'not_listed', 'sanctions_list': matches, 'source': self.source, 'as_of': self.as_of}


class DataEncryption:
    """Authenticated Fernet encryption; caller owns key persistence/rotation."""
    def __init__(self, key=None):
        from cryptography.fernet import Fernet
        key = key or os.getenv('DATA_ENCRYPTION_KEY')
        if key is None:
            raise ValueError('Provide DATA_ENCRYPTION_KEY or an explicit key; no implicit ephemeral persistence key')
        self.cipher = Fernet(key.encode() if isinstance(key, str) else key)

    @staticmethod
    def generate_key():
        from cryptography.fernet import Fernet
        return Fernet.generate_key()

    def encrypt(self, value):
        if not isinstance(value, str): raise TypeError('Expected string')
        return self.cipher.encrypt(value.encode()).decode()

    def decrypt(self, value):
        return self.cipher.decrypt(value.encode()).decode()


class GDPRCompliance:
    """Local subject record export/deletion, not a system-wide legal attestation.

    Blockchain records and retained audit records are not this store. Callers
    must coordinate retention/legal holds and other deployed data processors.
    """
    def __init__(self, path=None):
        if path is None:
            raise ValueError('Explicit subject database required')
        self.connection = sqlite3.connect(str(path))
        self.connection.execute('CREATE TABLE IF NOT EXISTS subjects(subject TEXT PRIMARY KEY,payload TEXT NOT NULL)')
        self.connection.commit()

    def store_user_data(self, user, data):
        if not user: raise ValueError('Subject required')
        with self.connection:
            self.connection.execute('INSERT OR REPLACE INTO subjects VALUES (?,?)', (user, json.dumps(data, allow_nan=False)))

    def export_user_data(self, user):
        row = self.connection.execute('SELECT payload FROM subjects WHERE subject=?', (user,)).fetchone()
        return {'subject': user, 'data_sources': ['local_subject_store'], 'data': json.loads(row[0]) if row else None, 'scope': 'local subject database only'}

    def delete_user_data(self, user):
        with self.connection:
            deleted = self.connection.execute('DELETE FROM subjects WHERE subject=?', (user,)).rowcount
        return {'success': True, 'deleted_records': deleted, 'deletion_timestamp': _now(), 'scope': 'local subject database only'}

    def close(self):
        self.connection.close()
