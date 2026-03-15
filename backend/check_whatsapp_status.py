"""
Check WhatsApp conversation flow and statistics
"""
import asyncio
from src.database.client import init_db_pool, close_db_pool, get_db_connection

async def check_whatsapp_flow():
    await init_db_pool()
    async with get_db_connection() as conn:
        # Get WhatsApp conversation with all details
        result = await conn.fetch('''
            SELECT
                c.phone,
                c.name,
                conv.id as conversation_id,
                m.role,
                m.content,
                m.created_at,
                t.id as ticket_id,
                t.status as ticket_status,
                t.priority,
                t.category
            FROM customers c
            JOIN conversations conv ON c.id = conv.customer_id
            JOIN messages m ON conv.id = m.conversation_id
            LEFT JOIN tickets t ON conv.id = t.conversation_id
            WHERE conv.initial_channel = 'whatsapp'
            AND c.phone = '+923152068370'
            ORDER BY m.created_at DESC
            LIMIT 10
        ''')

        print('WhatsApp Conversation Flow - Complete Test Results:')
        print('=' * 70)

        if not result:
            print('No WhatsApp messages found for +923152068370')
        else:
            current_conv = None
            for row in result:
                if current_conv != row['conversation_id']:
                    current_conv = row['conversation_id']
                    print(f'\nCustomer: {row["name"]} ({row["phone"]})')
                    print(f'Conversation ID: {str(row["conversation_id"])[:8]}...')
                    if row['ticket_id']:
                        print(f'Ticket ID: {str(row["ticket_id"])[:8]}...')
                        print(f'Status: {row["ticket_status"]} | Priority: {row["priority"]} | Category: {row["category"]}')
                    print('-' * 70)

                role_label = '[CUSTOMER]' if row['role'] == 'customer' else '[AGENT]'
                content = row['content'][:150] + '...' if len(row['content']) > 150 else row['content']
                print(f'{role_label} {content}')
                print(f'   Time: {row["created_at"]}')
                print()

        # Count statistics
        stats = await conn.fetchrow('''
            SELECT
                COUNT(DISTINCT c.id) as total_customers,
                COUNT(DISTINCT conv.id) as total_conversations,
                COUNT(m.id) as total_messages,
                COUNT(DISTINCT t.id) as total_tickets
            FROM customers c
            JOIN conversations conv ON c.id = conv.customer_id
            JOIN messages m ON conv.id = m.conversation_id
            LEFT JOIN tickets t ON conv.id = t.conversation_id
            WHERE conv.initial_channel = 'whatsapp'
        ''')

        print('=' * 70)
        print('WhatsApp Channel Statistics:')
        print(f'  Customers: {stats["total_customers"]}')
        print(f'  Conversations: {stats["total_conversations"]}')
        print(f'  Messages: {stats["total_messages"]}')
        print(f'  Tickets Created: {stats["total_tickets"]}')
        print('=' * 70)

    await close_db_pool()

if __name__ == '__main__':
    asyncio.run(check_whatsapp_flow())
