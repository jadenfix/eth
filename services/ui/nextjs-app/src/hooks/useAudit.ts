import { useAuth } from './useAuth'

export const useAudit = () => {
  const { user } = useAuth()

  const logEvent = async (action: string, details: Record<string, any>) => {
    try {
      const response = await fetch('/api/audit/log', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action,
          details,
          timestamp: new Date().toISOString(),
        }),
      })

      if (!response.ok) {
        console.error('Failed to log audit event')
      }
    } catch (error) {
      console.error('Audit logging error:', error)
    }
  }

  const logDataAccess = async (resourceType: string, resourceId: string, accessType: string) => {
    await logEvent('DATA_ACCESS', {
      resource_type: resourceType,
      resource_id: resourceId,
      access_type: accessType,
    })
  }

  const logUserAction = async (action: string, details: Record<string, any>) => {
    await logEvent(action, {
      ...details,
      user_id: user?.id,
    })
  }

  const logAdminAction = async (action: string, details: Record<string, any>) => {
    await logEvent(action, {
      ...details,
      user_id: user?.id,
      is_admin_action: true,
    })
  }

  return {
    logEvent,
    logDataAccess,
    logUserAction,
    logAdminAction,
  }
} 