/**
 * Test Better Auth Directly
 * This will help us see the actual error
 */

import { auth } from './src/lib/auth.js';

async function testBetterAuth() {
  console.log('Testing Better Auth configuration...\n');

  try {
    console.log('1. Checking auth object...');
    console.log('Auth object exists:', !!auth);
    console.log('Auth type:', typeof auth);

    console.log('\n2. Testing session retrieval...');
    // Try to get session (this is what's failing)
    const result = await auth.api.getSession({
      headers: new Headers(),
    });

    console.log('Session result:', result);
    console.log('✅ Better Auth working!');
  } catch (error) {
    console.error('\n❌ Better Auth error:');
    console.error('Message:', error.message);
    console.error('Stack:', error.stack);
  }
}

testBetterAuth();
