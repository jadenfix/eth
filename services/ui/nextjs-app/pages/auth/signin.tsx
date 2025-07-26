import React, { useState } from 'react'
import { signIn, getSession } from 'next-auth/react'
import { useRouter } from 'next/router'
import {
  Box,
  VStack,
  HStack,
  Text,
  Input,
  InputGroup,
  InputLeftElement,
  Button,
  FormControl,
  FormLabel,
  FormErrorMessage,
  useToast,
  Card,
  CardBody,
  Heading,
  Alert,
  AlertIcon
} from '@chakra-ui/react'
import { FiLock, FiMail } from 'react-icons/fi'

export default function SignIn() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const router = useRouter()
  const toast = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const result = await signIn('credentials', {
        email,
        password,
        redirect: false
      })

      if (result?.error) {
        setError('Invalid email or password')
        toast({
          title: 'Sign in failed',
          description: 'Please check your credentials and try again',
          status: 'error',
          duration: 5000
        })
      } else {
        toast({
          title: 'Sign in successful',
          description: 'Welcome to Onchain Command Center',
          status: 'success',
          duration: 3000
        })
        
        // Redirect to dashboard
        router.push('/')
      }
    } catch (error) {
      console.error('Sign in error:', error)
      setError('An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box
      minH="100vh"
      bg="gray.50"
      display="flex"
      alignItems="center"
      justifyContent="center"
      p={4}
    >
      <Card maxW="400px" w="full">
        <CardBody p={8}>
          <VStack spacing={6}>
            <VStack spacing={2}>
              <Heading size="lg">Onchain Command Center</Heading>
              <Text color="gray.600">Sign in to your account</Text>
            </VStack>

            {error && (
              <Alert status="error" borderRadius="md">
                <AlertIcon />
                {error}
              </Alert>
            )}

            <Box as="form" w="full" onSubmit={handleSubmit}>
              <VStack spacing={4}>
                <FormControl isInvalid={!!error}>
                  <FormLabel>Email</FormLabel>
                  <InputGroup>
                    <InputLeftElement>
                      <FiMail />
                    </InputLeftElement>
                    <Input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email"
                      required
                    />
                  </InputGroup>
                </FormControl>

                <FormControl isInvalid={!!error}>
                  <FormLabel>Password</FormLabel>
                  <InputGroup>
                    <InputLeftElement>
                      <FiLock />
                    </InputLeftElement>
                    <Input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      required
                    />
                  </InputGroup>
                  {error && <FormErrorMessage>{error}</FormErrorMessage>}
                </FormControl>

                <Button
                  type="submit"
                  colorScheme="blue"
                  size="lg"
                  w="full"
                  isLoading={loading}
                  loadingText="Signing in..."
                >
                  Sign In
                </Button>
              </VStack>
            </Box>

            <Text fontSize="sm" color="gray.500" textAlign="center">
              Demo credentials: admin@onchain.com / admin123
            </Text>
          </VStack>
        </CardBody>
      </Card>
    </Box>
  )
}

export async function getServerSideProps(context: any) {
  const session = await getSession(context)

  if (session) {
    return {
      redirect: {
        destination: '/',
        permanent: false
      }
    }
  }

  return {
    props: {}
  }
} 