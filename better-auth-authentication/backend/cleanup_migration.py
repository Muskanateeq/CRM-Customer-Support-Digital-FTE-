from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:postgres@localhost:5432/tasknest')
with engine.connect() as conn:
    tables = [
        'task_dependencies',
        'task_assignments',
        'comments',
        'team_members',
        'team_invitations',
        'milestones',
        'teams',
        'projects',
        'notifications',
        'notification_preferences',
        'custom_reports',
        'analytics_snapshots'
    ]

    for table in tables:
        conn.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE'))
        print(f'Dropped {table}')

    conn.commit()
    print('Cleanup complete')
