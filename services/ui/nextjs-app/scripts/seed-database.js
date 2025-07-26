const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcryptjs');

const prisma = new PrismaClient();

async function seedDatabase() {
  try {
    console.log('🌱 Seeding database...');

    // Create roles
    const adminRole = await prisma.role.upsert({
      where: { name: 'admin' },
      update: {},
      create: {
        name: 'admin',
        permissions: [
          'read:all',
          'write:all',
          'delete:all',
          'admin:users',
          'admin:system',
          'admin:audit'
        ]
      }
    });

    const analystRole = await prisma.role.upsert({
      where: { name: 'analyst' },
      update: {},
      create: {
        name: 'analyst',
        permissions: [
          'read:all',
          'write:analytics',
          'write:reports',
          'read:audit'
        ]
      }
    });

    const viewerRole = await prisma.role.upsert({
      where: { name: 'viewer' },
      update: {},
      create: {
        name: 'viewer',
        permissions: [
          'read:dashboard',
          'read:analytics',
          'read:reports'
        ]
      }
    });

    console.log('✅ Roles created');

    // Create users
    const adminPassword = await bcrypt.hash('admin123', 10);
    const analystPassword = await bcrypt.hash('analyst123', 10);
    const viewerPassword = await bcrypt.hash('viewer123', 10);

    const adminUser = await prisma.user.upsert({
      where: { email: 'admin@onchain.com' },
      update: {},
      create: {
        email: 'admin@onchain.com',
        name: 'Admin User',
        password: adminPassword,
        roleId: adminRole.id
      }
    });

    const analystUser = await prisma.user.upsert({
      where: { email: 'analyst@onchain.com' },
      update: {},
      create: {
        email: 'analyst@onchain.com',
        name: 'Analyst User',
        password: analystPassword,
        roleId: analystRole.id
      }
    });

    const viewerUser = await prisma.user.upsert({
      where: { email: 'viewer@onchain.com' },
      update: {},
      create: {
        email: 'viewer@onchain.com',
        name: 'Viewer User',
        password: viewerPassword,
        roleId: viewerRole.id
      }
    });

    console.log('✅ Users created');

    console.log('\n📋 Demo Credentials:');
    console.log('Admin: admin@onchain.com / admin123');
    console.log('Analyst: analyst@onchain.com / analyst123');
    console.log('Viewer: viewer@onchain.com / viewer123');

    console.log('\n🎉 Database seeding completed!');

  } catch (error) {
    console.error('❌ Error seeding database:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

seedDatabase(); 