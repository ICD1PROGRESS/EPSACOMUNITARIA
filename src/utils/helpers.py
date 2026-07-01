def get_periodo_activo(session, epsa_id):
    ultima = session.exec(select(Lectura).where(Lectura.epsa_id == epsa_id).order_by(Lectura.periodo.desc())).first()
    return ultima.periodo if ultima else "SIN PERIODO"