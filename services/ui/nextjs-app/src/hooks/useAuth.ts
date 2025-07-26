import { useSession } from 'next-auth/react'
import { useMemo } from 'react'

export const useAuth = () => {
  const { data: session, status } = useSession()

  const user = session?.user
  const isAuthenticated = !!user
  const isLoading = status === 'loading'

  const hasPermission = (permission: string): boolean => {
    if (!user?.permissions) return false
    return user.permissions.includes(permission)
  }

  const hasRole = (role: string): boolean => {
    if (!user?.role) return false
    return user.role === role
  }

  const isAdmin = useMemo(() => hasRole('admin'), [user?.role])
  const isAnalyst = useMemo(() => hasRole('analyst'), [user?.role])
  const isViewer = useMemo(() => hasRole('viewer'), [user?.role])

  return {
    user,
    isAuthenticated,
    isLoading,
    hasPermission,
    hasRole,
    isAdmin,
    isAnalyst,
    isViewer
  }
} 