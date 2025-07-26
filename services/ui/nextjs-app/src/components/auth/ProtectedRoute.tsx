import React from 'react'
import { useAuth } from '../../hooks/useAuth'
import { useRouter } from 'next/router'
import { Box, Spinner, Text, VStack } from '@chakra-ui/react'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: string
  requiredPermission?: string
  fallback?: React.ReactNode
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  requiredPermission,
  fallback
}) => {
  const { isAuthenticated, isLoading, hasRole, hasPermission } = useAuth()
  const router = useRouter()

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        minH="100vh"
      >
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text>Loading...</Text>
        </VStack>
      </Box>
    )
  }

  // Redirect to sign in if not authenticated
  if (!isAuthenticated) {
    router.push('/auth/signin')
    return null
  }

  // Check role requirement
  if (requiredRole && !hasRole(requiredRole)) {
    if (fallback) {
      return <>{fallback}</>
    }
    return (
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        minH="100vh"
      >
        <VStack spacing={4}>
          <Text fontSize="xl" fontWeight="bold">
            Access Denied
          </Text>
          <Text color="gray.600">
            You don't have the required role: {requiredRole}
          </Text>
        </VStack>
      </Box>
    )
  }

  // Check permission requirement
  if (requiredPermission && !hasPermission(requiredPermission)) {
    if (fallback) {
      return <>{fallback}</>
    }
    return (
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        minH="100vh"
      >
        <VStack spacing={4}>
          <Text fontSize="xl" fontWeight="bold">
            Access Denied
          </Text>
          <Text color="gray.600">
            You don't have the required permission: {requiredPermission}
          </Text>
        </VStack>
      </Box>
    )
  }

  return <>{children}</>
} 