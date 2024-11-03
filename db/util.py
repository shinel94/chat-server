def insert_data(session, instance):
    try:
        session.add(instance)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
