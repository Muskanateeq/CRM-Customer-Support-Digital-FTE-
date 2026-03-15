/**
 * Test Database Connection
 * Run this to verify Neon database is accessible
 */

const { Pool } = require('pg');
require('dotenv').config({ path: '.env.local' });

async function testConnection() {
  console.log('Testing Neon database connection...');
  console.log('DATABASE_URL:', process.env.DATABASE_URL ? 'SET' : 'NOT SET');

  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: {
      rejectUnauthorized: false,
    },
  });

  try {
    console.log('\n1. Connecting to database...');
    const client = await pool.connect();
    console.log('✅ Connected successfully!');

    console.log('\n2. Checking Better Auth tables...');
    const result = await client.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      AND table_name IN ('user', 'session', 'account', 'verification')
      ORDER BY table_name;
    `);

    console.log('Found tables:', result.rows.map(r => r.table_name));

    if (result.rows.length === 4) {
      console.log('✅ All Better Auth tables exist!');
    } else {
      console.log('❌ Missing tables:', ['user', 'session', 'account', 'verification'].filter(
        t => !result.rows.find(r => r.table_name === t)
      ));
    }

    console.log('\n3. Checking user table structure...');
    const userTable = await client.query(`
      SELECT column_name, data_type
      FROM information_schema.columns
      WHERE table_name = 'user'
      ORDER BY ordinal_position;
    `);
    console.log('User table columns:', userTable.rows);

    client.release();
    await pool.end();
    console.log('\n✅ Test complete!');
  } catch (error) {
    console.error('\n❌ Database connection failed:');
    console.error('Error:', error.message);
    console.error('\nPossible causes:');
    console.error('1. Database is sleeping (Neon free tier)');
    console.error('2. Invalid credentials');
    console.error('3. Network/firewall issue');
    console.error('4. Tables not created yet');
    await pool.end();
    process.exit(1);
  }
}

testConnection();
