import NextAuth, { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'

const prisma = new PrismaClient()

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        try {
          const user = await prisma.user.findUnique({
            where: { email: credentials.email },
            include: { role: true }
          })

          if (!user) {
            return null
          }

          const isPasswordValid = await bcrypt.compare(credentials.password, user.password)

          if (!isPasswordValid) {
            return null
          }

          return {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role.name,
            permissions: user.role.permissions
          }
        } catch (error) {
          console.error('Auth error:', error)
          return null
        }
      }
    })
  ],
  session: {
    strategy: 'jwt',
    maxAge: 24 * 60 * 60, // 24 hours
  },
  jwt: {
    secret: process.env.NEXTAUTH_SECRET,
    encode: async ({ secret, token }) => {
      if (!token) return ''
      
      const encodedToken = jwt.sign(
        {
          ...token,
          role: token.role,
          permissions: token.permissions
        },
        secret,
        { expiresIn: '24h' }
      )
      return encodedToken
    },
    decode: async ({ secret, token }) => {
      if (!token) return null
      
      try {
        const decodedToken = jwt.verify(token, secret) as any
        return decodedToken
      } catch (error) {
        console.error('JWT decode error:', error)
        return null
      }
    }
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role
        token.permissions = user.permissions
      }
      return token
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.sub
        session.user.role = token.role
        session.user.permissions = token.permissions
      }
      return session
    },
    async signIn({ user, account, profile }) {
      // Log sign-in attempt
      await prisma.auditLog.create({
        data: {
          userId: user.id,
          action: 'SIGN_IN',
          details: {
            provider: account?.provider || 'credentials',
            timestamp: new Date().toISOString()
          }
        }
      })
      return true
    }
  },
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error'
  },
  secret: process.env.NEXTAUTH_SECRET
}

export default NextAuth(authOptions) 