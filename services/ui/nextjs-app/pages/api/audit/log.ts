import { NextApiRequest, NextApiResponse } from 'next'
import { getSession } from 'next-auth/react'
import { audit_service } from '../../../../../services/access_control/audit_service'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    // Get user session
    const session = await getSession({ req })
    
    if (!session?.user?.id) {
      return res.status(401).json({ error: 'Unauthorized' })
    }

    const { action, details, resource_type, resource_id, severity = 'INFO' } = req.body

    if (!action || !details) {
      return res.status(400).json({ error: 'Action and details are required' })
    }

    // Get client IP and user agent
    const ip_address = req.headers['x-forwarded-for'] as string || 
                      req.connection.remoteAddress || 
                      req.socket.remoteAddress
    const user_agent = req.headers['user-agent']

    // Log the audit event
    const success = await audit_service.log_user_action(
      session.user.id,
      action,
      details,
      ip_address,
      user_agent
    )

    if (success) {
      res.status(200).json({ success: true, message: 'Audit event logged successfully' })
    } else {
      res.status(500).json({ error: 'Failed to log audit event' })
    }

  } catch (error) {
    console.error('Audit logging error:', error)
    res.status(500).json({ error: 'Internal server error' })
  }
} 