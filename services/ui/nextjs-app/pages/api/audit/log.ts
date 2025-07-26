import { NextApiRequest, NextApiResponse } from 'next'
import { getServerSession } from 'next-auth'
import { authOptions } from '../auth/[...nextauth]'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    // Verify user session
    const session = await getServerSession(req, res, authOptions)
    if (!session) {
      return res.status(401).json({ error: 'Unauthorized' })
    }

    const { action, details, timestamp } = req.body

    // Call the audit service via HTTP
    const auditResponse = await fetch('http://localhost:4001/audit/log', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action,
        details: {
          ...details,
          user_id: session.user.id,
        },
        timestamp,
      }),
    })

    if (!auditResponse.ok) {
      throw new Error('Failed to log audit event')
    }

    res.status(200).json({ success: true })
  } catch (error) {
    console.error('Audit logging error:', error)
    res.status(500).json({ error: 'Internal server error' })
  }
} 