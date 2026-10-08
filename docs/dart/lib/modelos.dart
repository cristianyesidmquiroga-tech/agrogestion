// Generado por scripts/exportar_contrato.py desde openapi.json. No editar a mano.
// Los listados cerrados (estados, tipos, roles) son String; sus valores están
// en mobile_api_contract.md.

class ActividadCreate {
  final String cicloId;
  final String nombre;
  final String fase;
  final DateTime fechaInicio;
  final DateTime? fechaFin;
  final double areaTrabajada;

  const ActividadCreate({
    required this.cicloId,
    required this.nombre,
    required this.fase,
    required this.fechaInicio,
    this.fechaFin,
    required this.areaTrabajada,
  });

  factory ActividadCreate.fromJson(Map<String, dynamic> json) => ActividadCreate(
        cicloId: json['ciclo_id'] as String,
        nombre: json['nombre'] as String,
        fase: json['fase'] as String,
        fechaInicio: DateTime.parse(json['fecha_inicio'] as String),
        fechaFin: json['fecha_fin'] == null ? null : DateTime.parse(json['fecha_fin'] as String),
        areaTrabajada: (json['area_trabajada'] as num).toDouble(),
      );

  Map<String, dynamic> toJson() => {
        'ciclo_id': cicloId,
        'nombre': nombre,
        'fase': fase,
        'fecha_inicio': fechaInicio.toUtc().toIso8601String(),
        if (fechaFin != null) 'fecha_fin': fechaFin!.toUtc().toIso8601String(),
        'area_trabajada': areaTrabajada,
      };
}

class ActividadResponse {
  final String id;
  final String fincaId;
  final String cicloId;
  final String nombre;
  final String fase;
  final DateTime fechaInicio;
  final DateTime? fechaFin;
  final String areaTrabajada;
  final String estado;

  const ActividadResponse({
    required this.id,
    required this.fincaId,
    required this.cicloId,
    required this.nombre,
    required this.fase,
    required this.fechaInicio,
    this.fechaFin,
    required this.areaTrabajada,
    required this.estado,
  });

  factory ActividadResponse.fromJson(Map<String, dynamic> json) => ActividadResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        cicloId: json['ciclo_id'] as String,
        nombre: json['nombre'] as String,
        fase: json['fase'] as String,
        fechaInicio: DateTime.parse(json['fecha_inicio'] as String),
        fechaFin: json['fecha_fin'] == null ? null : DateTime.parse(json['fecha_fin'] as String),
        areaTrabajada: json['area_trabajada'] as String,
        estado: json['estado'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'ciclo_id': cicloId,
        'nombre': nombre,
        'fase': fase,
        'fecha_inicio': fechaInicio.toUtc().toIso8601String(),
        if (fechaFin != null) 'fecha_fin': fechaFin!.toUtc().toIso8601String(),
        'area_trabajada': areaTrabajada,
        'estado': estado,
      };
}

class ActividadUpdate {
  final String? nombre;
  final String? fase;
  final DateTime? fechaFin;
  final double? areaTrabajada;

  const ActividadUpdate({
    this.nombre,
    this.fase,
    this.fechaFin,
    this.areaTrabajada,
  });

  factory ActividadUpdate.fromJson(Map<String, dynamic> json) => ActividadUpdate(
        nombre: json['nombre'] == null ? null : json['nombre'] as String,
        fase: json['fase'] == null ? null : json['fase'] as String,
        fechaFin: json['fecha_fin'] == null ? null : DateTime.parse(json['fecha_fin'] as String),
        areaTrabajada: json['area_trabajada'] == null ? null : (json['area_trabajada'] as num).toDouble(),
      );

  Map<String, dynamic> toJson() => {
        if (nombre != null) 'nombre': nombre!,
        if (fase != null) 'fase': fase!,
        if (fechaFin != null) 'fecha_fin': fechaFin!.toUtc().toIso8601String(),
        if (areaTrabajada != null) 'area_trabajada': areaTrabajada!,
      };
}

class AlertaCreate {
  final String fuenteId;
  final String tipo;
  final String regionDane;
  final String titulo;
  final String resumen;
  final DateTime vigenteDesde;
  final DateTime vigenteHasta;

  const AlertaCreate({
    required this.fuenteId,
    required this.tipo,
    required this.regionDane,
    required this.titulo,
    required this.resumen,
    required this.vigenteDesde,
    required this.vigenteHasta,
  });

  factory AlertaCreate.fromJson(Map<String, dynamic> json) => AlertaCreate(
        fuenteId: json['fuente_id'] as String,
        tipo: json['tipo'] as String,
        regionDane: json['region_dane'] as String,
        titulo: json['titulo'] as String,
        resumen: json['resumen'] as String,
        vigenteDesde: DateTime.parse(json['vigente_desde'] as String),
        vigenteHasta: DateTime.parse(json['vigente_hasta'] as String),
      );

  Map<String, dynamic> toJson() => {
        'fuente_id': fuenteId,
        'tipo': tipo,
        'region_dane': regionDane,
        'titulo': titulo,
        'resumen': resumen,
        'vigente_desde': vigenteDesde.toUtc().toIso8601String(),
        'vigente_hasta': vigenteHasta.toUtc().toIso8601String(),
      };
}

class AlertaResponse {
  final String id;
  final String fincaId;
  final String fuenteId;
  final String tipo;
  final String regionDane;
  final String titulo;
  final String resumen;
  final DateTime vigenteDesde;
  final DateTime vigenteHasta;

  const AlertaResponse({
    required this.id,
    required this.fincaId,
    required this.fuenteId,
    required this.tipo,
    required this.regionDane,
    required this.titulo,
    required this.resumen,
    required this.vigenteDesde,
    required this.vigenteHasta,
  });

  factory AlertaResponse.fromJson(Map<String, dynamic> json) => AlertaResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        fuenteId: json['fuente_id'] as String,
        tipo: json['tipo'] as String,
        regionDane: json['region_dane'] as String,
        titulo: json['titulo'] as String,
        resumen: json['resumen'] as String,
        vigenteDesde: DateTime.parse(json['vigente_desde'] as String),
        vigenteHasta: DateTime.parse(json['vigente_hasta'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'fuente_id': fuenteId,
        'tipo': tipo,
        'region_dane': regionDane,
        'titulo': titulo,
        'resumen': resumen,
        'vigente_desde': vigenteDesde.toUtc().toIso8601String(),
        'vigente_hasta': vigenteHasta.toUtc().toIso8601String(),
      };
}

class AlimentacionCreate {
  final String loteAnimalId;
  final String alimento;
  final double cantidad;
  final double costo;
  final DateTime fecha;

  const AlimentacionCreate({
    required this.loteAnimalId,
    required this.alimento,
    required this.cantidad,
    required this.costo,
    required this.fecha,
  });

  factory AlimentacionCreate.fromJson(Map<String, dynamic> json) => AlimentacionCreate(
        loteAnimalId: json['lote_animal_id'] as String,
        alimento: json['alimento'] as String,
        cantidad: (json['cantidad'] as num).toDouble(),
        costo: (json['costo'] as num).toDouble(),
        fecha: DateTime.parse(json['fecha'] as String),
      );

  Map<String, dynamic> toJson() => {
        'lote_animal_id': loteAnimalId,
        'alimento': alimento,
        'cantidad': cantidad,
        'costo': costo,
        'fecha': fecha.toUtc().toIso8601String(),
      };
}

class AlimentacionResponse {
  final String id;
  final String fincaId;
  final String loteAnimalId;
  final String alimento;
  final String cantidad;
  final String costo;
  final DateTime fecha;

  const AlimentacionResponse({
    required this.id,
    required this.fincaId,
    required this.loteAnimalId,
    required this.alimento,
    required this.cantidad,
    required this.costo,
    required this.fecha,
  });

  factory AlimentacionResponse.fromJson(Map<String, dynamic> json) => AlimentacionResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        loteAnimalId: json['lote_animal_id'] as String,
        alimento: json['alimento'] as String,
        cantidad: json['cantidad'] as String,
        costo: json['costo'] as String,
        fecha: DateTime.parse(json['fecha'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'lote_animal_id': loteAnimalId,
        'alimento': alimento,
        'cantidad': cantidad,
        'costo': costo,
        'fecha': fecha.toUtc().toIso8601String(),
      };
}

class AnimalCreate {
  final String especieId;
  final String? loteAnimalId;
  final String arete;
  final String? nombre;
  final String sexo;
  final String? raza;
  final DateTime? nacimiento;
  final String? madreId;
  final String? padreId;

  const AnimalCreate({
    required this.especieId,
    this.loteAnimalId,
    required this.arete,
    this.nombre,
    required this.sexo,
    this.raza,
    this.nacimiento,
    this.madreId,
    this.padreId,
  });

  factory AnimalCreate.fromJson(Map<String, dynamic> json) => AnimalCreate(
        especieId: json['especie_id'] as String,
        loteAnimalId: json['lote_animal_id'] == null ? null : json['lote_animal_id'] as String,
        arete: json['arete'] as String,
        nombre: json['nombre'] == null ? null : json['nombre'] as String,
        sexo: json['sexo'] as String,
        raza: json['raza'] == null ? null : json['raza'] as String,
        nacimiento: json['nacimiento'] == null ? null : DateTime.parse(json['nacimiento'] as String),
        madreId: json['madre_id'] == null ? null : json['madre_id'] as String,
        padreId: json['padre_id'] == null ? null : json['padre_id'] as String,
      );

  Map<String, dynamic> toJson() => {
        'especie_id': especieId,
        if (loteAnimalId != null) 'lote_animal_id': loteAnimalId!,
        'arete': arete,
        if (nombre != null) 'nombre': nombre!,
        'sexo': sexo,
        if (raza != null) 'raza': raza!,
        if (nacimiento != null) 'nacimiento': nacimiento!.toUtc().toIso8601String(),
        if (madreId != null) 'madre_id': madreId!,
        if (padreId != null) 'padre_id': padreId!,
      };
}

class AnimalResponse {
  final String id;
  final String fincaId;
  final String especieId;
  final String? loteAnimalId;
  final String arete;
  final String? nombre;
  final String sexo;
  final String? raza;
  final DateTime? nacimiento;
  final String? madreId;
  final String? padreId;
  final String estado;

  const AnimalResponse({
    required this.id,
    required this.fincaId,
    required this.especieId,
    this.loteAnimalId,
    required this.arete,
    this.nombre,
    required this.sexo,
    this.raza,
    this.nacimiento,
    this.madreId,
    this.padreId,
    required this.estado,
  });

  factory AnimalResponse.fromJson(Map<String, dynamic> json) => AnimalResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        especieId: json['especie_id'] as String,
        loteAnimalId: json['lote_animal_id'] == null ? null : json['lote_animal_id'] as String,
        arete: json['arete'] as String,
        nombre: json['nombre'] == null ? null : json['nombre'] as String,
        sexo: json['sexo'] as String,
        raza: json['raza'] == null ? null : json['raza'] as String,
        nacimiento: json['nacimiento'] == null ? null : DateTime.parse(json['nacimiento'] as String),
        madreId: json['madre_id'] == null ? null : json['madre_id'] as String,
        padreId: json['padre_id'] == null ? null : json['padre_id'] as String,
        estado: json['estado'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'especie_id': especieId,
        if (loteAnimalId != null) 'lote_animal_id': loteAnimalId!,
        'arete': arete,
        if (nombre != null) 'nombre': nombre!,
        'sexo': sexo,
        if (raza != null) 'raza': raza!,
        if (nacimiento != null) 'nacimiento': nacimiento!.toUtc().toIso8601String(),
        if (madreId != null) 'madre_id': madreId!,
        if (padreId != null) 'padre_id': padreId!,
        'estado': estado,
      };
}

class AnulacionCreate {
  final String motivo;

  const AnulacionCreate({
    required this.motivo,
  });

  factory AnulacionCreate.fromJson(Map<String, dynamic> json) => AnulacionCreate(
        motivo: json['motivo'] as String,
      );

  Map<String, dynamic> toJson() => {
        'motivo': motivo,
      };
}

class AvisoRiesgo {
  final String siembraId;
  final String cicloId;
  final String cultivo;
  final String fase;
  final String riesgo;
  final String susceptibilidad;
  final String? medidas;
  final bool porValidar;
  final String texto;

  const AvisoRiesgo({
    required this.siembraId,
    required this.cicloId,
    required this.cultivo,
    required this.fase,
    required this.riesgo,
    required this.susceptibilidad,
    this.medidas,
    required this.porValidar,
    required this.texto,
  });

  factory AvisoRiesgo.fromJson(Map<String, dynamic> json) => AvisoRiesgo(
        siembraId: json['siembra_id'] as String,
        cicloId: json['ciclo_id'] as String,
        cultivo: json['cultivo'] as String,
        fase: json['fase'] as String,
        riesgo: json['riesgo'] as String,
        susceptibilidad: json['susceptibilidad'] as String,
        medidas: json['medidas'] == null ? null : json['medidas'] as String,
        porValidar: json['por_validar'] as bool,
        texto: json['texto'] as String,
      );

  Map<String, dynamic> toJson() => {
        'siembra_id': siembraId,
        'ciclo_id': cicloId,
        'cultivo': cultivo,
        'fase': fase,
        'riesgo': riesgo,
        'susceptibilidad': susceptibilidad,
        if (medidas != null) 'medidas': medidas!,
        'por_validar': porValidar,
        'texto': texto,
      };
}

class AvisosSalida {
  final List<AvisoRiesgo> avisos;
  final int siembrasSinCalendario;
  final String? aviso;

  const AvisosSalida({
    required this.avisos,
    required this.siembrasSinCalendario,
    this.aviso,
  });

  factory AvisosSalida.fromJson(Map<String, dynamic> json) => AvisosSalida(
        avisos: (json['avisos'] as List<dynamic>).map((x) => AvisoRiesgo.fromJson(x as Map<String, dynamic>)).toList(),
        siembrasSinCalendario: json['siembras_sin_calendario'] as int,
        aviso: json['aviso'] == null ? null : json['aviso'] as String,
      );

  Map<String, dynamic> toJson() => {
        'avisos': avisos.map((x) => x.toJson()).toList(),
        'siembras_sin_calendario': siembrasSinCalendario,
        if (aviso != null) 'aviso': aviso!,
      };
}

class CalidadSalida {
  final int consultas;
  final int conValoracion;
  final int sirvieron;
  final int noSirvieron;
  final int equivocadas;
  final double? porcentajeQueSirvio;
  final String? aviso;

  const CalidadSalida({
    required this.consultas,
    required this.conValoracion,
    required this.sirvieron,
    required this.noSirvieron,
    required this.equivocadas,
    this.porcentajeQueSirvio,
    this.aviso,
  });

  factory CalidadSalida.fromJson(Map<String, dynamic> json) => CalidadSalida(
        consultas: json['consultas'] as int,
        conValoracion: json['con_valoracion'] as int,
        sirvieron: json['sirvieron'] as int,
        noSirvieron: json['no_sirvieron'] as int,
        equivocadas: json['equivocadas'] as int,
        porcentajeQueSirvio: json['porcentaje_que_sirvio'] == null ? null : (json['porcentaje_que_sirvio'] as num).toDouble(),
        aviso: json['aviso'] == null ? null : json['aviso'] as String,
      );

  Map<String, dynamic> toJson() => {
        'consultas': consultas,
        'con_valoracion': conValoracion,
        'sirvieron': sirvieron,
        'no_sirvieron': noSirvieron,
        'equivocadas': equivocadas,
        if (porcentajeQueSirvio != null) 'porcentaje_que_sirvio': porcentajeQueSirvio!,
        if (aviso != null) 'aviso': aviso!,
      };
}

class CambiarEstado {
  final String estado;
  final String? observacion;

  const CambiarEstado({
    required this.estado,
    this.observacion,
  });

  factory CambiarEstado.fromJson(Map<String, dynamic> json) => CambiarEstado(
        estado: json['estado'] as String,
        observacion: json['observacion'] == null ? null : json['observacion'] as String,
      );

  Map<String, dynamic> toJson() => {
        'estado': estado,
        if (observacion != null) 'observacion': observacion!,
      };
}

class CausaProbable {
  final String problemaId;
  final String problema;
  final String coincidencia;
  final String porQue;
  final List<String> fuentes;

  const CausaProbable({
    required this.problemaId,
    required this.problema,
    required this.coincidencia,
    required this.porQue,
    required this.fuentes,
  });

  factory CausaProbable.fromJson(Map<String, dynamic> json) => CausaProbable(
        problemaId: json['problema_id'] as String,
        problema: json['problema'] as String,
        coincidencia: json['coincidencia'] as String,
        porQue: json['por_que'] as String,
        fuentes: (json['fuentes'] as List<dynamic>).map((x) => x as String).toList(),
      );

  Map<String, dynamic> toJson() => {
        'problema_id': problemaId,
        'problema': problema,
        'coincidencia': coincidencia,
        'por_que': porQue,
        'fuentes': fuentes.map((x) => x).toList(),
      };
}

class CerrarCicloEntrada {
  final String? motivoPerdida;
  final DateTime? fechaFin;

  const CerrarCicloEntrada({
    this.motivoPerdida,
    this.fechaFin,
  });

  factory CerrarCicloEntrada.fromJson(Map<String, dynamic> json) => CerrarCicloEntrada(
        motivoPerdida: json['motivo_perdida'] == null ? null : json['motivo_perdida'] as String,
        fechaFin: json['fecha_fin'] == null ? null : DateTime.parse(json['fecha_fin'] as String),
      );

  Map<String, dynamic> toJson() => {
        if (motivoPerdida != null) 'motivo_perdida': motivoPerdida!,
        if (fechaFin != null) 'fecha_fin': fechaFin!.toIso8601String().substring(0, 10),
      };
}

class CicloCrear {
  final String tipo;

  const CicloCrear({
    required this.tipo,
  });

  factory CicloCrear.fromJson(Map<String, dynamic> json) => CicloCrear(
        tipo: json['tipo'] as String,
      );

  Map<String, dynamic> toJson() => {
        'tipo': tipo,
      };
}

class CicloCreate {
  final String nombre;
  final DateTime fechaInicio;
  final DateTime? fechaFin;

  const CicloCreate({
    required this.nombre,
    required this.fechaInicio,
    this.fechaFin,
  });

  factory CicloCreate.fromJson(Map<String, dynamic> json) => CicloCreate(
        nombre: json['nombre'] as String,
        fechaInicio: DateTime.parse(json['fecha_inicio'] as String),
        fechaFin: json['fecha_fin'] == null ? null : DateTime.parse(json['fecha_fin'] as String),
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        'fecha_inicio': fechaInicio.toUtc().toIso8601String(),
        if (fechaFin != null) 'fecha_fin': fechaFin!.toUtc().toIso8601String(),
      };
}

class CicloCronograma {
  final String siembraId;
  final String cicloId;
  final String cultivo;
  final String tipo;
  final DateTime? fechaInicio;
  final String? faseActual;
  final int fasesPlaneadas;
  final DateTime? fechaFinPlaneada;
  final String? aviso;

  const CicloCronograma({
    required this.siembraId,
    required this.cicloId,
    required this.cultivo,
    required this.tipo,
    this.fechaInicio,
    this.faseActual,
    required this.fasesPlaneadas,
    this.fechaFinPlaneada,
    this.aviso,
  });

  factory CicloCronograma.fromJson(Map<String, dynamic> json) => CicloCronograma(
        siembraId: json['siembra_id'] as String,
        cicloId: json['ciclo_id'] as String,
        cultivo: json['cultivo'] as String,
        tipo: json['tipo'] as String,
        fechaInicio: json['fecha_inicio'] == null ? null : DateTime.parse(json['fecha_inicio'] as String),
        faseActual: json['fase_actual'] == null ? null : json['fase_actual'] as String,
        fasesPlaneadas: json['fases_planeadas'] as int,
        fechaFinPlaneada: json['fecha_fin_planeada'] == null ? null : DateTime.parse(json['fecha_fin_planeada'] as String),
        aviso: json['aviso'] == null ? null : json['aviso'] as String,
      );

  Map<String, dynamic> toJson() => {
        'siembra_id': siembraId,
        'ciclo_id': cicloId,
        'cultivo': cultivo,
        'tipo': tipo,
        if (fechaInicio != null) 'fecha_inicio': fechaInicio!.toIso8601String().substring(0, 10),
        if (faseActual != null) 'fase_actual': faseActual!,
        'fases_planeadas': fasesPlaneadas,
        if (fechaFinPlaneada != null) 'fecha_fin_planeada': fechaFinPlaneada!.toIso8601String().substring(0, 10),
        if (aviso != null) 'aviso': aviso!,
      };
}

class CicloResponse {
  final String id;
  final String fincaId;
  final String nombre;
  final String estado;
  final DateTime fechaInicio;
  final DateTime? fechaFin;

  const CicloResponse({
    required this.id,
    required this.fincaId,
    required this.nombre,
    required this.estado,
    required this.fechaInicio,
    this.fechaFin,
  });

  factory CicloResponse.fromJson(Map<String, dynamic> json) => CicloResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        nombre: json['nombre'] as String,
        estado: json['estado'] as String,
        fechaInicio: DateTime.parse(json['fecha_inicio'] as String),
        fechaFin: json['fecha_fin'] == null ? null : DateTime.parse(json['fecha_fin'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'nombre': nombre,
        'estado': estado,
        'fecha_inicio': fechaInicio.toUtc().toIso8601String(),
        if (fechaFin != null) 'fecha_fin': fechaFin!.toUtc().toIso8601String(),
      };
}

class CicloSalida {
  final String id;
  final String tipo;
  final int numero;
  final String estado;
  final DateTime? fechaInicio;
  final DateTime? fechaFin;
  final String? motivoPerdida;

  const CicloSalida({
    required this.id,
    required this.tipo,
    required this.numero,
    required this.estado,
    this.fechaInicio,
    this.fechaFin,
    this.motivoPerdida,
  });

  factory CicloSalida.fromJson(Map<String, dynamic> json) => CicloSalida(
        id: json['id'] as String,
        tipo: json['tipo'] as String,
        numero: json['numero'] as int,
        estado: json['estado'] as String,
        fechaInicio: json['fecha_inicio'] == null ? null : DateTime.parse(json['fecha_inicio'] as String),
        fechaFin: json['fecha_fin'] == null ? null : DateTime.parse(json['fecha_fin'] as String),
        motivoPerdida: json['motivo_perdida'] == null ? null : json['motivo_perdida'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'tipo': tipo,
        'numero': numero,
        'estado': estado,
        if (fechaInicio != null) 'fecha_inicio': fechaInicio!.toIso8601String().substring(0, 10),
        if (fechaFin != null) 'fecha_fin': fechaFin!.toIso8601String().substring(0, 10),
        if (motivoPerdida != null) 'motivo_perdida': motivoPerdida!,
      };
}

class ConsentimientoEntrada {
  final String versionPolitica;
  final bool aceptaTratamiento;
  final bool? aceptaTransferenciaIa;

  const ConsentimientoEntrada({
    required this.versionPolitica,
    required this.aceptaTratamiento,
    this.aceptaTransferenciaIa,
  });

  factory ConsentimientoEntrada.fromJson(Map<String, dynamic> json) => ConsentimientoEntrada(
        versionPolitica: json['version_politica'] as String,
        aceptaTratamiento: json['acepta_tratamiento'] as bool,
        aceptaTransferenciaIa: json['acepta_transferencia_ia'] == null ? null : json['acepta_transferencia_ia'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'version_politica': versionPolitica,
        'acepta_tratamiento': aceptaTratamiento,
        if (aceptaTransferenciaIa != null) 'acepta_transferencia_ia': aceptaTransferenciaIa!,
      };
}

class ConsentimientoSalida {
  final String versionPolitica;
  final DateTime aceptadoEn;
  final bool aceptaTransferenciaIa;

  const ConsentimientoSalida({
    required this.versionPolitica,
    required this.aceptadoEn,
    required this.aceptaTransferenciaIa,
  });

  factory ConsentimientoSalida.fromJson(Map<String, dynamic> json) => ConsentimientoSalida(
        versionPolitica: json['version_politica'] as String,
        aceptadoEn: DateTime.parse(json['aceptado_en'] as String),
        aceptaTransferenciaIa: json['acepta_transferencia_ia'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'version_politica': versionPolitica,
        'aceptado_en': aceptadoEn.toUtc().toIso8601String(),
        'acepta_transferencia_ia': aceptaTransferenciaIa,
      };
}

class ConsultaCrear {
  final String siembraId;
  final String texto;

  const ConsultaCrear({
    required this.siembraId,
    required this.texto,
  });

  factory ConsultaCrear.fromJson(Map<String, dynamic> json) => ConsultaCrear(
        siembraId: json['siembra_id'] as String,
        texto: json['texto'] as String,
      );

  Map<String, dynamic> toJson() => {
        'siembra_id': siembraId,
        'texto': texto,
      };
}

class ConsultaResumen {
  final String id;
  final String contextoId;
  final DateTime creadoEn;
  final String pregunta;
  final String? valoracion;

  const ConsultaResumen({
    required this.id,
    required this.contextoId,
    required this.creadoEn,
    required this.pregunta,
    this.valoracion,
  });

  factory ConsultaResumen.fromJson(Map<String, dynamic> json) => ConsultaResumen(
        id: json['id'] as String,
        contextoId: json['contexto_id'] as String,
        creadoEn: DateTime.parse(json['creado_en'] as String),
        pregunta: json['pregunta'] as String,
        valoracion: json['valoracion'] == null ? null : json['valoracion'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'contexto_id': contextoId,
        'creado_en': creadoEn.toUtc().toIso8601String(),
        'pregunta': pregunta,
        if (valoracion != null) 'valoracion': valoracion!,
      };
}

class ConsultaSalida {
  final String id;
  final String contexto;
  final String contextoId;
  final DateTime creadoEn;
  final String pregunta;
  final RespuestaAsistente respuesta;
  final String mensajeRespuestaId;
  final String? valoracion;

  const ConsultaSalida({
    required this.id,
    required this.contexto,
    required this.contextoId,
    required this.creadoEn,
    required this.pregunta,
    required this.respuesta,
    required this.mensajeRespuestaId,
    this.valoracion,
  });

  factory ConsultaSalida.fromJson(Map<String, dynamic> json) => ConsultaSalida(
        id: json['id'] as String,
        contexto: json['contexto'] as String,
        contextoId: json['contexto_id'] as String,
        creadoEn: DateTime.parse(json['creado_en'] as String),
        pregunta: json['pregunta'] as String,
        respuesta: RespuestaAsistente.fromJson(json['respuesta'] as Map<String, dynamic>),
        mensajeRespuestaId: json['mensaje_respuesta_id'] as String,
        valoracion: json['valoracion'] == null ? null : json['valoracion'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'contexto': contexto,
        'contexto_id': contextoId,
        'creado_en': creadoEn.toUtc().toIso8601String(),
        'pregunta': pregunta,
        'respuesta': respuesta.toJson(),
        'mensaje_respuesta_id': mensajeRespuestaId,
        if (valoracion != null) 'valoracion': valoracion!,
      };
}

class ContableResponse {
  final String id;
  final String fincaId;
  final String categoria;
  final String? monto;
  final String? total;
  final String estado;

  const ContableResponse({
    required this.id,
    required this.fincaId,
    required this.categoria,
    this.monto,
    this.total,
    required this.estado,
  });

  factory ContableResponse.fromJson(Map<String, dynamic> json) => ContableResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        categoria: json['categoria'] as String,
        monto: json['monto'] == null ? null : json['monto'] as String,
        total: json['total'] == null ? null : json['total'] as String,
        estado: json['estado'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'categoria': categoria,
        if (monto != null) 'monto': monto!,
        if (total != null) 'total': total!,
        'estado': estado,
      };
}

class ConteoCrear {
  final DateTime fecha;
  final int vivas;
  final int? muertas;
  final int? resiembras;

  const ConteoCrear({
    required this.fecha,
    required this.vivas,
    this.muertas,
    this.resiembras,
  });

  factory ConteoCrear.fromJson(Map<String, dynamic> json) => ConteoCrear(
        fecha: DateTime.parse(json['fecha'] as String),
        vivas: json['vivas'] as int,
        muertas: json['muertas'] == null ? null : json['muertas'] as int,
        resiembras: json['resiembras'] == null ? null : json['resiembras'] as int,
      );

  Map<String, dynamic> toJson() => {
        'fecha': fecha.toIso8601String().substring(0, 10),
        'vivas': vivas,
        if (muertas != null) 'muertas': muertas!,
        if (resiembras != null) 'resiembras': resiembras!,
      };
}

class ConteoSalida {
  final String id;
  final DateTime fecha;
  final int vivas;
  final int muertas;
  final int resiembras;

  const ConteoSalida({
    required this.id,
    required this.fecha,
    required this.vivas,
    required this.muertas,
    required this.resiembras,
  });

  factory ConteoSalida.fromJson(Map<String, dynamic> json) => ConteoSalida(
        id: json['id'] as String,
        fecha: DateTime.parse(json['fecha'] as String),
        vivas: json['vivas'] as int,
        muertas: json['muertas'] as int,
        resiembras: json['resiembras'] as int,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'fecha': fecha.toIso8601String().substring(0, 10),
        'vivas': vivas,
        'muertas': muertas,
        'resiembras': resiembras,
      };
}

class CosechaAcumuladoResponse {
  final String fincaId;
  final String cicloId;
  final String total;
  final List<CosechaResponse> registros;

  const CosechaAcumuladoResponse({
    required this.fincaId,
    required this.cicloId,
    required this.total,
    required this.registros,
  });

  factory CosechaAcumuladoResponse.fromJson(Map<String, dynamic> json) => CosechaAcumuladoResponse(
        fincaId: json['finca_id'] as String,
        cicloId: json['ciclo_id'] as String,
        total: json['total'] as String,
        registros: (json['registros'] as List<dynamic>).map((x) => CosechaResponse.fromJson(x as Map<String, dynamic>)).toList(),
      );

  Map<String, dynamic> toJson() => {
        'finca_id': fincaId,
        'ciclo_id': cicloId,
        'total': total,
        'registros': registros.map((x) => x.toJson()).toList(),
      };
}

class CosechaCreate {
  final String cicloId;
  final double cantidad;
  final String unidad;
  final String? calidad;
  final DateTime fecha;

  const CosechaCreate({
    required this.cicloId,
    required this.cantidad,
    required this.unidad,
    this.calidad,
    required this.fecha,
  });

  factory CosechaCreate.fromJson(Map<String, dynamic> json) => CosechaCreate(
        cicloId: json['ciclo_id'] as String,
        cantidad: (json['cantidad'] as num).toDouble(),
        unidad: json['unidad'] as String,
        calidad: json['calidad'] == null ? null : json['calidad'] as String,
        fecha: DateTime.parse(json['fecha'] as String),
      );

  Map<String, dynamic> toJson() => {
        'ciclo_id': cicloId,
        'cantidad': cantidad,
        'unidad': unidad,
        if (calidad != null) 'calidad': calidad!,
        'fecha': fecha.toUtc().toIso8601String(),
      };
}

class CosechaResponse {
  final String id;
  final String fincaId;
  final String cicloId;
  final String cantidad;
  final String unidad;
  final String? calidad;
  final DateTime fecha;

  const CosechaResponse({
    required this.id,
    required this.fincaId,
    required this.cicloId,
    required this.cantidad,
    required this.unidad,
    this.calidad,
    required this.fecha,
  });

  factory CosechaResponse.fromJson(Map<String, dynamic> json) => CosechaResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        cicloId: json['ciclo_id'] as String,
        cantidad: json['cantidad'] as String,
        unidad: json['unidad'] as String,
        calidad: json['calidad'] == null ? null : json['calidad'] as String,
        fecha: DateTime.parse(json['fecha'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'ciclo_id': cicloId,
        'cantidad': cantidad,
        'unidad': unidad,
        if (calidad != null) 'calidad': calidad!,
        'fecha': fecha.toUtc().toIso8601String(),
      };
}

class CronogramaSalida {
  final String cicloId;
  final String tipo;
  final DateTime? fechaInicio;
  final List<FaseCronograma> fases;
  final String? aviso;

  const CronogramaSalida({
    required this.cicloId,
    required this.tipo,
    this.fechaInicio,
    required this.fases,
    this.aviso,
  });

  factory CronogramaSalida.fromJson(Map<String, dynamic> json) => CronogramaSalida(
        cicloId: json['ciclo_id'] as String,
        tipo: json['tipo'] as String,
        fechaInicio: json['fecha_inicio'] == null ? null : DateTime.parse(json['fecha_inicio'] as String),
        fases: (json['fases'] as List<dynamic>).map((x) => FaseCronograma.fromJson(x as Map<String, dynamic>)).toList(),
        aviso: json['aviso'] == null ? null : json['aviso'] as String,
      );

  Map<String, dynamic> toJson() => {
        'ciclo_id': cicloId,
        'tipo': tipo,
        if (fechaInicio != null) 'fecha_inicio': fechaInicio!.toIso8601String().substring(0, 10),
        'fases': fases.map((x) => x.toJson()).toList(),
        if (aviso != null) 'aviso': aviso!,
      };
}

class CultivoActualizar {
  final String nombre;
  final String? nombreCientifico;
  final String grupo;
  final String tipoCiclo;
  final String unidadConteo;
  final String? tipoRenovacion;
  final String unidadCosecha;
  final String? pagoCosechaSugerido;
  final int? densidadRef;
  final int? mesesPrimeraCosecha;
  final double? cosechasPorAnio;
  final bool? porValidar;
  final String? fuente;
  final List<FaseEntrada>? fases;
  final List<MetodoEntrada>? metodos;
  final List<DosisEntrada>? dosis;

  const CultivoActualizar({
    required this.nombre,
    this.nombreCientifico,
    required this.grupo,
    required this.tipoCiclo,
    required this.unidadConteo,
    this.tipoRenovacion,
    required this.unidadCosecha,
    this.pagoCosechaSugerido,
    this.densidadRef,
    this.mesesPrimeraCosecha,
    this.cosechasPorAnio,
    this.porValidar,
    this.fuente,
    this.fases,
    this.metodos,
    this.dosis,
  });

  factory CultivoActualizar.fromJson(Map<String, dynamic> json) => CultivoActualizar(
        nombre: json['nombre'] as String,
        nombreCientifico: json['nombre_cientifico'] == null ? null : json['nombre_cientifico'] as String,
        grupo: json['grupo'] as String,
        tipoCiclo: json['tipo_ciclo'] as String,
        unidadConteo: json['unidad_conteo'] as String,
        tipoRenovacion: json['tipo_renovacion'] == null ? null : json['tipo_renovacion'] as String,
        unidadCosecha: json['unidad_cosecha'] as String,
        pagoCosechaSugerido: json['pago_cosecha_sugerido'] == null ? null : json['pago_cosecha_sugerido'] as String,
        densidadRef: json['densidad_ref'] == null ? null : json['densidad_ref'] as int,
        mesesPrimeraCosecha: json['meses_primera_cosecha'] == null ? null : json['meses_primera_cosecha'] as int,
        cosechasPorAnio: json['cosechas_por_anio'] == null ? null : (json['cosechas_por_anio'] as num).toDouble(),
        porValidar: json['por_validar'] == null ? null : json['por_validar'] as bool,
        fuente: json['fuente'] == null ? null : json['fuente'] as String,
        fases: json['fases'] == null ? null : (json['fases'] as List<dynamic>).map((x) => FaseEntrada.fromJson(x as Map<String, dynamic>)).toList(),
        metodos: json['metodos'] == null ? null : (json['metodos'] as List<dynamic>).map((x) => MetodoEntrada.fromJson(x as Map<String, dynamic>)).toList(),
        dosis: json['dosis'] == null ? null : (json['dosis'] as List<dynamic>).map((x) => DosisEntrada.fromJson(x as Map<String, dynamic>)).toList(),
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        if (nombreCientifico != null) 'nombre_cientifico': nombreCientifico!,
        'grupo': grupo,
        'tipo_ciclo': tipoCiclo,
        'unidad_conteo': unidadConteo,
        if (tipoRenovacion != null) 'tipo_renovacion': tipoRenovacion!,
        'unidad_cosecha': unidadCosecha,
        if (pagoCosechaSugerido != null) 'pago_cosecha_sugerido': pagoCosechaSugerido!,
        if (densidadRef != null) 'densidad_ref': densidadRef!,
        if (mesesPrimeraCosecha != null) 'meses_primera_cosecha': mesesPrimeraCosecha!,
        if (cosechasPorAnio != null) 'cosechas_por_anio': cosechasPorAnio!,
        if (porValidar != null) 'por_validar': porValidar!,
        if (fuente != null) 'fuente': fuente!,
        if (fases != null) 'fases': fases!.map((x) => x.toJson()).toList(),
        if (metodos != null) 'metodos': metodos!.map((x) => x.toJson()).toList(),
        if (dosis != null) 'dosis': dosis!.map((x) => x.toJson()).toList(),
      };
}

class CultivoCrear {
  final String nombre;
  final String? nombreCientifico;
  final String grupo;
  final String tipoCiclo;
  final String unidadConteo;
  final String? tipoRenovacion;
  final String unidadCosecha;
  final String? pagoCosechaSugerido;
  final int? densidadRef;
  final int? mesesPrimeraCosecha;
  final double? cosechasPorAnio;
  final bool? porValidar;
  final String? fuente;
  final List<FaseEntrada>? fases;
  final List<MetodoEntrada>? metodos;
  final List<DosisEntrada>? dosis;
  final String? copiarDe;

  const CultivoCrear({
    required this.nombre,
    this.nombreCientifico,
    required this.grupo,
    required this.tipoCiclo,
    required this.unidadConteo,
    this.tipoRenovacion,
    required this.unidadCosecha,
    this.pagoCosechaSugerido,
    this.densidadRef,
    this.mesesPrimeraCosecha,
    this.cosechasPorAnio,
    this.porValidar,
    this.fuente,
    this.fases,
    this.metodos,
    this.dosis,
    this.copiarDe,
  });

  factory CultivoCrear.fromJson(Map<String, dynamic> json) => CultivoCrear(
        nombre: json['nombre'] as String,
        nombreCientifico: json['nombre_cientifico'] == null ? null : json['nombre_cientifico'] as String,
        grupo: json['grupo'] as String,
        tipoCiclo: json['tipo_ciclo'] as String,
        unidadConteo: json['unidad_conteo'] as String,
        tipoRenovacion: json['tipo_renovacion'] == null ? null : json['tipo_renovacion'] as String,
        unidadCosecha: json['unidad_cosecha'] as String,
        pagoCosechaSugerido: json['pago_cosecha_sugerido'] == null ? null : json['pago_cosecha_sugerido'] as String,
        densidadRef: json['densidad_ref'] == null ? null : json['densidad_ref'] as int,
        mesesPrimeraCosecha: json['meses_primera_cosecha'] == null ? null : json['meses_primera_cosecha'] as int,
        cosechasPorAnio: json['cosechas_por_anio'] == null ? null : (json['cosechas_por_anio'] as num).toDouble(),
        porValidar: json['por_validar'] == null ? null : json['por_validar'] as bool,
        fuente: json['fuente'] == null ? null : json['fuente'] as String,
        fases: json['fases'] == null ? null : (json['fases'] as List<dynamic>).map((x) => FaseEntrada.fromJson(x as Map<String, dynamic>)).toList(),
        metodos: json['metodos'] == null ? null : (json['metodos'] as List<dynamic>).map((x) => MetodoEntrada.fromJson(x as Map<String, dynamic>)).toList(),
        dosis: json['dosis'] == null ? null : (json['dosis'] as List<dynamic>).map((x) => DosisEntrada.fromJson(x as Map<String, dynamic>)).toList(),
        copiarDe: json['copiar_de'] == null ? null : json['copiar_de'] as String,
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        if (nombreCientifico != null) 'nombre_cientifico': nombreCientifico!,
        'grupo': grupo,
        'tipo_ciclo': tipoCiclo,
        'unidad_conteo': unidadConteo,
        if (tipoRenovacion != null) 'tipo_renovacion': tipoRenovacion!,
        'unidad_cosecha': unidadCosecha,
        if (pagoCosechaSugerido != null) 'pago_cosecha_sugerido': pagoCosechaSugerido!,
        if (densidadRef != null) 'densidad_ref': densidadRef!,
        if (mesesPrimeraCosecha != null) 'meses_primera_cosecha': mesesPrimeraCosecha!,
        if (cosechasPorAnio != null) 'cosechas_por_anio': cosechasPorAnio!,
        if (porValidar != null) 'por_validar': porValidar!,
        if (fuente != null) 'fuente': fuente!,
        if (fases != null) 'fases': fases!.map((x) => x.toJson()).toList(),
        if (metodos != null) 'metodos': metodos!.map((x) => x.toJson()).toList(),
        if (dosis != null) 'dosis': dosis!.map((x) => x.toJson()).toList(),
        if (copiarDe != null) 'copiar_de': copiarDe!,
      };
}

class CultivoResumen {
  final String id;
  final String nombre;
  final String grupo;
  final String tipoCiclo;
  final String unidadConteo;
  final bool porValidar;

  const CultivoResumen({
    required this.id,
    required this.nombre,
    required this.grupo,
    required this.tipoCiclo,
    required this.unidadConteo,
    required this.porValidar,
  });

  factory CultivoResumen.fromJson(Map<String, dynamic> json) => CultivoResumen(
        id: json['id'] as String,
        nombre: json['nombre'] as String,
        grupo: json['grupo'] as String,
        tipoCiclo: json['tipo_ciclo'] as String,
        unidadConteo: json['unidad_conteo'] as String,
        porValidar: json['por_validar'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'nombre': nombre,
        'grupo': grupo,
        'tipo_ciclo': tipoCiclo,
        'unidad_conteo': unidadConteo,
        'por_validar': porValidar,
      };
}

class CultivoRiesgoEntrada {
  final String riesgoId;
  final String? faseCritica;
  final String susceptibilidad;
  final String? medidas;
  final bool? porValidar;

  const CultivoRiesgoEntrada({
    required this.riesgoId,
    this.faseCritica,
    required this.susceptibilidad,
    this.medidas,
    this.porValidar,
  });

  factory CultivoRiesgoEntrada.fromJson(Map<String, dynamic> json) => CultivoRiesgoEntrada(
        riesgoId: json['riesgo_id'] as String,
        faseCritica: json['fase_critica'] == null ? null : json['fase_critica'] as String,
        susceptibilidad: json['susceptibilidad'] as String,
        medidas: json['medidas'] == null ? null : json['medidas'] as String,
        porValidar: json['por_validar'] == null ? null : json['por_validar'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'riesgo_id': riesgoId,
        if (faseCritica != null) 'fase_critica': faseCritica!,
        'susceptibilidad': susceptibilidad,
        if (medidas != null) 'medidas': medidas!,
        if (porValidar != null) 'por_validar': porValidar!,
      };
}

class CultivoRiesgoSalida {
  final String riesgoId;
  final String? faseCritica;
  final String susceptibilidad;
  final String? medidas;
  final bool porValidar;

  const CultivoRiesgoSalida({
    required this.riesgoId,
    this.faseCritica,
    required this.susceptibilidad,
    this.medidas,
    required this.porValidar,
  });

  factory CultivoRiesgoSalida.fromJson(Map<String, dynamic> json) => CultivoRiesgoSalida(
        riesgoId: json['riesgo_id'] as String,
        faseCritica: json['fase_critica'] == null ? null : json['fase_critica'] as String,
        susceptibilidad: json['susceptibilidad'] as String,
        medidas: json['medidas'] == null ? null : json['medidas'] as String,
        porValidar: json['por_validar'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'riesgo_id': riesgoId,
        if (faseCritica != null) 'fase_critica': faseCritica!,
        'susceptibilidad': susceptibilidad,
        if (medidas != null) 'medidas': medidas!,
        'por_validar': porValidar,
      };
}

class CultivoSalida {
  final String id;
  final String nombre;
  final String grupo;
  final String tipoCiclo;
  final String unidadConteo;
  final bool porValidar;
  final String? nombreCientifico;
  final String? tipoRenovacion;
  final String unidadCosecha;
  final String? pagoCosechaSugerido;
  final int? densidadRef;
  final int? mesesPrimeraCosecha;
  final double? cosechasPorAnio;
  final String? fuente;
  final List<FaseSalida> fases;
  final List<MetodoSalida> metodos;
  final List<DosisSalida> dosis;

  const CultivoSalida({
    required this.id,
    required this.nombre,
    required this.grupo,
    required this.tipoCiclo,
    required this.unidadConteo,
    required this.porValidar,
    this.nombreCientifico,
    this.tipoRenovacion,
    required this.unidadCosecha,
    this.pagoCosechaSugerido,
    this.densidadRef,
    this.mesesPrimeraCosecha,
    this.cosechasPorAnio,
    this.fuente,
    required this.fases,
    required this.metodos,
    required this.dosis,
  });

  factory CultivoSalida.fromJson(Map<String, dynamic> json) => CultivoSalida(
        id: json['id'] as String,
        nombre: json['nombre'] as String,
        grupo: json['grupo'] as String,
        tipoCiclo: json['tipo_ciclo'] as String,
        unidadConteo: json['unidad_conteo'] as String,
        porValidar: json['por_validar'] as bool,
        nombreCientifico: json['nombre_cientifico'] == null ? null : json['nombre_cientifico'] as String,
        tipoRenovacion: json['tipo_renovacion'] == null ? null : json['tipo_renovacion'] as String,
        unidadCosecha: json['unidad_cosecha'] as String,
        pagoCosechaSugerido: json['pago_cosecha_sugerido'] == null ? null : json['pago_cosecha_sugerido'] as String,
        densidadRef: json['densidad_ref'] == null ? null : json['densidad_ref'] as int,
        mesesPrimeraCosecha: json['meses_primera_cosecha'] == null ? null : json['meses_primera_cosecha'] as int,
        cosechasPorAnio: json['cosechas_por_anio'] == null ? null : (json['cosechas_por_anio'] as num).toDouble(),
        fuente: json['fuente'] == null ? null : json['fuente'] as String,
        fases: (json['fases'] as List<dynamic>).map((x) => FaseSalida.fromJson(x as Map<String, dynamic>)).toList(),
        metodos: (json['metodos'] as List<dynamic>).map((x) => MetodoSalida.fromJson(x as Map<String, dynamic>)).toList(),
        dosis: (json['dosis'] as List<dynamic>).map((x) => DosisSalida.fromJson(x as Map<String, dynamic>)).toList(),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'nombre': nombre,
        'grupo': grupo,
        'tipo_ciclo': tipoCiclo,
        'unidad_conteo': unidadConteo,
        'por_validar': porValidar,
        if (nombreCientifico != null) 'nombre_cientifico': nombreCientifico!,
        if (tipoRenovacion != null) 'tipo_renovacion': tipoRenovacion!,
        'unidad_cosecha': unidadCosecha,
        if (pagoCosechaSugerido != null) 'pago_cosecha_sugerido': pagoCosechaSugerido!,
        if (densidadRef != null) 'densidad_ref': densidadRef!,
        if (mesesPrimeraCosecha != null) 'meses_primera_cosecha': mesesPrimeraCosecha!,
        if (cosechasPorAnio != null) 'cosechas_por_anio': cosechasPorAnio!,
        if (fuente != null) 'fuente': fuente!,
        'fases': fases.map((x) => x.toJson()).toList(),
        'metodos': metodos.map((x) => x.toJson()).toList(),
        'dosis': dosis.map((x) => x.toJson()).toList(),
      };
}

class DetalleError {
  final String campo;
  final String mensaje;
  final String tipo;

  const DetalleError({
    required this.campo,
    required this.mensaje,
    required this.tipo,
  });

  factory DetalleError.fromJson(Map<String, dynamic> json) => DetalleError(
        campo: json['campo'] as String,
        mensaje: json['mensaje'] as String,
        tipo: json['tipo'] as String,
      );

  Map<String, dynamic> toJson() => {
        'campo': campo,
        'mensaje': mensaje,
        'tipo': tipo,
      };
}

class DosisEntrada {
  final String insumoTipo;
  final double dosis;
  final String unidad;
  final String base;
  final bool? porValidar;

  const DosisEntrada({
    required this.insumoTipo,
    required this.dosis,
    required this.unidad,
    required this.base,
    this.porValidar,
  });

  factory DosisEntrada.fromJson(Map<String, dynamic> json) => DosisEntrada(
        insumoTipo: json['insumo_tipo'] as String,
        dosis: (json['dosis'] as num).toDouble(),
        unidad: json['unidad'] as String,
        base: json['base'] as String,
        porValidar: json['por_validar'] == null ? null : json['por_validar'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'insumo_tipo': insumoTipo,
        'dosis': dosis,
        'unidad': unidad,
        'base': base,
        if (porValidar != null) 'por_validar': porValidar!,
      };
}

class DosisSalida {
  final String insumoTipo;
  final double dosis;
  final String unidad;
  final String base;
  final bool porValidar;

  const DosisSalida({
    required this.insumoTipo,
    required this.dosis,
    required this.unidad,
    required this.base,
    required this.porValidar,
  });

  factory DosisSalida.fromJson(Map<String, dynamic> json) => DosisSalida(
        insumoTipo: json['insumo_tipo'] as String,
        dosis: (json['dosis'] as num).toDouble(),
        unidad: json['unidad'] as String,
        base: json['base'] as String,
        porValidar: json['por_validar'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'insumo_tipo': insumoTipo,
        'dosis': dosis,
        'unidad': unidad,
        'base': base,
        'por_validar': porValidar,
      };
}

class ErrorDetalle {
  final String code;
  final String message;
  final String? action;
  final List<DetalleError>? details;

  const ErrorDetalle({
    required this.code,
    required this.message,
    this.action,
    this.details,
  });

  factory ErrorDetalle.fromJson(Map<String, dynamic> json) => ErrorDetalle(
        code: json['code'] as String,
        message: json['message'] as String,
        action: json['action'] == null ? null : json['action'] as String,
        details: json['details'] == null ? null : (json['details'] as List<dynamic>).map((x) => DetalleError.fromJson(x as Map<String, dynamic>)).toList(),
      );

  Map<String, dynamic> toJson() => {
        'code': code,
        'message': message,
        if (action != null) 'action': action!,
        if (details != null) 'details': details!.map((x) => x.toJson()).toList(),
      };
}

class ErrorRespuesta {
  final ErrorDetalle error;

  const ErrorRespuesta({
    required this.error,
  });

  factory ErrorRespuesta.fromJson(Map<String, dynamic> json) => ErrorRespuesta(
        error: ErrorDetalle.fromJson(json['error'] as Map<String, dynamic>),
      );

  Map<String, dynamic> toJson() => {
        'error': error.toJson(),
      };
}

class EspecieCreate {
  final String nombre;
  final String? descripcion;

  const EspecieCreate({
    required this.nombre,
    this.descripcion,
  });

  factory EspecieCreate.fromJson(Map<String, dynamic> json) => EspecieCreate(
        nombre: json['nombre'] as String,
        descripcion: json['descripcion'] == null ? null : json['descripcion'] as String,
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        if (descripcion != null) 'descripcion': descripcion!,
      };
}

class EspecieResponse {
  final String id;
  final String fincaId;
  final String nombre;
  final String? descripcion;

  const EspecieResponse({
    required this.id,
    required this.fincaId,
    required this.nombre,
    this.descripcion,
  });

  factory EspecieResponse.fromJson(Map<String, dynamic> json) => EspecieResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        nombre: json['nombre'] as String,
        descripcion: json['descripcion'] == null ? null : json['descripcion'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'nombre': nombre,
        if (descripcion != null) 'descripcion': descripcion!,
      };
}

class EtapaCreate {
  final String nombre;
  final double diasEstimados;

  const EtapaCreate({
    required this.nombre,
    required this.diasEstimados,
  });

  factory EtapaCreate.fromJson(Map<String, dynamic> json) => EtapaCreate(
        nombre: json['nombre'] as String,
        diasEstimados: (json['dias_estimados'] as num).toDouble(),
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        'dias_estimados': diasEstimados,
      };
}

class EtapaResponse {
  final String id;
  final String procesoId;
  final String fincaId;
  final String nombre;
  final String diasEstimados;
  final DateTime? iniciadoEn;
  final DateTime? finalizadoEn;

  const EtapaResponse({
    required this.id,
    required this.procesoId,
    required this.fincaId,
    required this.nombre,
    required this.diasEstimados,
    this.iniciadoEn,
    this.finalizadoEn,
  });

  factory EtapaResponse.fromJson(Map<String, dynamic> json) => EtapaResponse(
        id: json['id'] as String,
        procesoId: json['proceso_id'] as String,
        fincaId: json['finca_id'] as String,
        nombre: json['nombre'] as String,
        diasEstimados: json['dias_estimados'] as String,
        iniciadoEn: json['iniciado_en'] == null ? null : DateTime.parse(json['iniciado_en'] as String),
        finalizadoEn: json['finalizado_en'] == null ? null : DateTime.parse(json['finalizado_en'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'proceso_id': procesoId,
        'finca_id': fincaId,
        'nombre': nombre,
        'dias_estimados': diasEstimados,
        if (iniciadoEn != null) 'iniciado_en': iniciadoEn!.toUtc().toIso8601String(),
        if (finalizadoEn != null) 'finalizado_en': finalizadoEn!.toUtc().toIso8601String(),
      };
}

class EtapasMetricasResponse {
  final String procesoId;
  final String diasEstimados;
  final String diasReales;
  final String diferencia;

  const EtapasMetricasResponse({
    required this.procesoId,
    required this.diasEstimados,
    required this.diasReales,
    required this.diferencia,
  });

  factory EtapasMetricasResponse.fromJson(Map<String, dynamic> json) => EtapasMetricasResponse(
        procesoId: json['proceso_id'] as String,
        diasEstimados: json['dias_estimados'] as String,
        diasReales: json['dias_reales'] as String,
        diferencia: json['diferencia'] as String,
      );

  Map<String, dynamic> toJson() => {
        'proceso_id': procesoId,
        'dias_estimados': diasEstimados,
        'dias_reales': diasReales,
        'diferencia': diferencia,
      };
}

class EventoActualizar {
  final DateTime? fin;
  final String? severidad;
  final double? areaAfectada;
  final double? perdidaPct;
  final double? perdidaEstimada;
  final String? notas;

  const EventoActualizar({
    this.fin,
    this.severidad,
    this.areaAfectada,
    this.perdidaPct,
    this.perdidaEstimada,
    this.notas,
  });

  factory EventoActualizar.fromJson(Map<String, dynamic> json) => EventoActualizar(
        fin: json['fin'] == null ? null : DateTime.parse(json['fin'] as String),
        severidad: json['severidad'] == null ? null : json['severidad'] as String,
        areaAfectada: json['area_afectada'] == null ? null : (json['area_afectada'] as num).toDouble(),
        perdidaPct: json['perdida_pct'] == null ? null : (json['perdida_pct'] as num).toDouble(),
        perdidaEstimada: json['perdida_estimada'] == null ? null : (json['perdida_estimada'] as num).toDouble(),
        notas: json['notas'] == null ? null : json['notas'] as String,
      );

  Map<String, dynamic> toJson() => {
        if (fin != null) 'fin': fin!.toIso8601String().substring(0, 10),
        if (severidad != null) 'severidad': severidad!,
        if (areaAfectada != null) 'area_afectada': areaAfectada!,
        if (perdidaPct != null) 'perdida_pct': perdidaPct!,
        if (perdidaEstimada != null) 'perdida_estimada': perdidaEstimada!,
        if (notas != null) 'notas': notas!,
      };
}

class EventoCrear {
  final String fincaId;
  final String riesgoId;
  final String? siembraId;
  final String? cicloId;
  final DateTime inicio;
  final DateTime? fin;
  final String severidad;
  final double? areaAfectada;
  final double? perdidaPct;
  final double? perdidaEstimada;
  final String? notas;

  const EventoCrear({
    required this.fincaId,
    required this.riesgoId,
    this.siembraId,
    this.cicloId,
    required this.inicio,
    this.fin,
    required this.severidad,
    this.areaAfectada,
    this.perdidaPct,
    this.perdidaEstimada,
    this.notas,
  });

  factory EventoCrear.fromJson(Map<String, dynamic> json) => EventoCrear(
        fincaId: json['finca_id'] as String,
        riesgoId: json['riesgo_id'] as String,
        siembraId: json['siembra_id'] == null ? null : json['siembra_id'] as String,
        cicloId: json['ciclo_id'] == null ? null : json['ciclo_id'] as String,
        inicio: DateTime.parse(json['inicio'] as String),
        fin: json['fin'] == null ? null : DateTime.parse(json['fin'] as String),
        severidad: json['severidad'] as String,
        areaAfectada: json['area_afectada'] == null ? null : (json['area_afectada'] as num).toDouble(),
        perdidaPct: json['perdida_pct'] == null ? null : (json['perdida_pct'] as num).toDouble(),
        perdidaEstimada: json['perdida_estimada'] == null ? null : (json['perdida_estimada'] as num).toDouble(),
        notas: json['notas'] == null ? null : json['notas'] as String,
      );

  Map<String, dynamic> toJson() => {
        'finca_id': fincaId,
        'riesgo_id': riesgoId,
        if (siembraId != null) 'siembra_id': siembraId!,
        if (cicloId != null) 'ciclo_id': cicloId!,
        'inicio': inicio.toIso8601String().substring(0, 10),
        if (fin != null) 'fin': fin!.toIso8601String().substring(0, 10),
        'severidad': severidad,
        if (areaAfectada != null) 'area_afectada': areaAfectada!,
        if (perdidaPct != null) 'perdida_pct': perdidaPct!,
        if (perdidaEstimada != null) 'perdida_estimada': perdidaEstimada!,
        if (notas != null) 'notas': notas!,
      };
}

class EventoCreate {
  final String? animalId;
  final String? loteAnimalId;
  final String tipo;
  final DateTime fecha;
  final String? producto;
  final double? dosis;
  final DateTime? retiroHasta;
  final String? notas;

  const EventoCreate({
    this.animalId,
    this.loteAnimalId,
    required this.tipo,
    required this.fecha,
    this.producto,
    this.dosis,
    this.retiroHasta,
    this.notas,
  });

  factory EventoCreate.fromJson(Map<String, dynamic> json) => EventoCreate(
        animalId: json['animal_id'] == null ? null : json['animal_id'] as String,
        loteAnimalId: json['lote_animal_id'] == null ? null : json['lote_animal_id'] as String,
        tipo: json['tipo'] as String,
        fecha: DateTime.parse(json['fecha'] as String),
        producto: json['producto'] == null ? null : json['producto'] as String,
        dosis: json['dosis'] == null ? null : (json['dosis'] as num).toDouble(),
        retiroHasta: json['retiro_hasta'] == null ? null : DateTime.parse(json['retiro_hasta'] as String),
        notas: json['notas'] == null ? null : json['notas'] as String,
      );

  Map<String, dynamic> toJson() => {
        if (animalId != null) 'animal_id': animalId!,
        if (loteAnimalId != null) 'lote_animal_id': loteAnimalId!,
        'tipo': tipo,
        'fecha': fecha.toUtc().toIso8601String(),
        if (producto != null) 'producto': producto!,
        if (dosis != null) 'dosis': dosis!,
        if (retiroHasta != null) 'retiro_hasta': retiroHasta!.toUtc().toIso8601String(),
        if (notas != null) 'notas': notas!,
      };
}

class EventoReciente {
  final String id;
  final String riesgo;
  final String severidad;
  final DateTime inicio;

  const EventoReciente({
    required this.id,
    required this.riesgo,
    required this.severidad,
    required this.inicio,
  });

  factory EventoReciente.fromJson(Map<String, dynamic> json) => EventoReciente(
        id: json['id'] as String,
        riesgo: json['riesgo'] as String,
        severidad: json['severidad'] as String,
        inicio: DateTime.parse(json['inicio'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'riesgo': riesgo,
        'severidad': severidad,
        'inicio': inicio.toIso8601String().substring(0, 10),
      };
}

class EventoResponse {
  final String id;
  final String fincaId;
  final String? animalId;
  final String? loteAnimalId;
  final String tipo;
  final DateTime fecha;
  final String? producto;
  final String? dosis;
  final DateTime? retiroHasta;
  final String? notas;

  const EventoResponse({
    required this.id,
    required this.fincaId,
    this.animalId,
    this.loteAnimalId,
    required this.tipo,
    required this.fecha,
    this.producto,
    this.dosis,
    this.retiroHasta,
    this.notas,
  });

  factory EventoResponse.fromJson(Map<String, dynamic> json) => EventoResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        animalId: json['animal_id'] == null ? null : json['animal_id'] as String,
        loteAnimalId: json['lote_animal_id'] == null ? null : json['lote_animal_id'] as String,
        tipo: json['tipo'] as String,
        fecha: DateTime.parse(json['fecha'] as String),
        producto: json['producto'] == null ? null : json['producto'] as String,
        dosis: json['dosis'] == null ? null : json['dosis'] as String,
        retiroHasta: json['retiro_hasta'] == null ? null : DateTime.parse(json['retiro_hasta'] as String),
        notas: json['notas'] == null ? null : json['notas'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        if (animalId != null) 'animal_id': animalId!,
        if (loteAnimalId != null) 'lote_animal_id': loteAnimalId!,
        'tipo': tipo,
        'fecha': fecha.toUtc().toIso8601String(),
        if (producto != null) 'producto': producto!,
        if (dosis != null) 'dosis': dosis!,
        if (retiroHasta != null) 'retiro_hasta': retiroHasta!.toUtc().toIso8601String(),
        if (notas != null) 'notas': notas!,
      };
}

class EventoSalida {
  final String id;
  final String fincaId;
  final String riesgoId;
  final String? siembraId;
  final String? cicloId;
  final DateTime inicio;
  final DateTime? fin;
  final String severidad;
  final double? areaAfectada;
  final double? perdidaPct;
  final double? perdidaEstimada;
  final String? notas;

  const EventoSalida({
    required this.id,
    required this.fincaId,
    required this.riesgoId,
    this.siembraId,
    this.cicloId,
    required this.inicio,
    this.fin,
    required this.severidad,
    this.areaAfectada,
    this.perdidaPct,
    this.perdidaEstimada,
    this.notas,
  });

  factory EventoSalida.fromJson(Map<String, dynamic> json) => EventoSalida(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        riesgoId: json['riesgo_id'] as String,
        siembraId: json['siembra_id'] == null ? null : json['siembra_id'] as String,
        cicloId: json['ciclo_id'] == null ? null : json['ciclo_id'] as String,
        inicio: DateTime.parse(json['inicio'] as String),
        fin: json['fin'] == null ? null : DateTime.parse(json['fin'] as String),
        severidad: json['severidad'] as String,
        areaAfectada: json['area_afectada'] == null ? null : (json['area_afectada'] as num).toDouble(),
        perdidaPct: json['perdida_pct'] == null ? null : (json['perdida_pct'] as num).toDouble(),
        perdidaEstimada: json['perdida_estimada'] == null ? null : (json['perdida_estimada'] as num).toDouble(),
        notas: json['notas'] == null ? null : json['notas'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'riesgo_id': riesgoId,
        if (siembraId != null) 'siembra_id': siembraId!,
        if (cicloId != null) 'ciclo_id': cicloId!,
        'inicio': inicio.toIso8601String().substring(0, 10),
        if (fin != null) 'fin': fin!.toIso8601String().substring(0, 10),
        'severidad': severidad,
        if (areaAfectada != null) 'area_afectada': areaAfectada!,
        if (perdidaPct != null) 'perdida_pct': perdidaPct!,
        if (perdidaEstimada != null) 'perdida_estimada': perdidaEstimada!,
        if (notas != null) 'notas': notas!,
      };
}

class EventosPorTipo {
  final String tipo;
  final int cantidad;
  final double perdidaEstimada;
  final double? perdidaPromedioPct;

  const EventosPorTipo({
    required this.tipo,
    required this.cantidad,
    required this.perdidaEstimada,
    this.perdidaPromedioPct,
  });

  factory EventosPorTipo.fromJson(Map<String, dynamic> json) => EventosPorTipo(
        tipo: json['tipo'] as String,
        cantidad: json['cantidad'] as int,
        perdidaEstimada: (json['perdida_estimada'] as num).toDouble(),
        perdidaPromedioPct: json['perdida_promedio_pct'] == null ? null : (json['perdida_promedio_pct'] as num).toDouble(),
      );

  Map<String, dynamic> toJson() => {
        'tipo': tipo,
        'cantidad': cantidad,
        'perdida_estimada': perdidaEstimada,
        if (perdidaPromedioPct != null) 'perdida_promedio_pct': perdidaPromedioPct!,
      };
}

class FaseCronograma {
  final String fase;
  final int orden;
  final int? diasEstimados;
  final bool porValidar;
  final DateTime? inicioPlan;
  final DateTime? finPlan;
  final DateTime? inicioReal;
  final DateTime? finReal;
  final int? diasRetraso;

  const FaseCronograma({
    required this.fase,
    required this.orden,
    this.diasEstimados,
    required this.porValidar,
    this.inicioPlan,
    this.finPlan,
    this.inicioReal,
    this.finReal,
    this.diasRetraso,
  });

  factory FaseCronograma.fromJson(Map<String, dynamic> json) => FaseCronograma(
        fase: json['fase'] as String,
        orden: json['orden'] as int,
        diasEstimados: json['dias_estimados'] == null ? null : json['dias_estimados'] as int,
        porValidar: json['por_validar'] as bool,
        inicioPlan: json['inicio_plan'] == null ? null : DateTime.parse(json['inicio_plan'] as String),
        finPlan: json['fin_plan'] == null ? null : DateTime.parse(json['fin_plan'] as String),
        inicioReal: json['inicio_real'] == null ? null : DateTime.parse(json['inicio_real'] as String),
        finReal: json['fin_real'] == null ? null : DateTime.parse(json['fin_real'] as String),
        diasRetraso: json['dias_retraso'] == null ? null : json['dias_retraso'] as int,
      );

  Map<String, dynamic> toJson() => {
        'fase': fase,
        'orden': orden,
        if (diasEstimados != null) 'dias_estimados': diasEstimados!,
        'por_validar': porValidar,
        if (inicioPlan != null) 'inicio_plan': inicioPlan!.toIso8601String().substring(0, 10),
        if (finPlan != null) 'fin_plan': finPlan!.toIso8601String().substring(0, 10),
        if (inicioReal != null) 'inicio_real': inicioReal!.toIso8601String().substring(0, 10),
        if (finReal != null) 'fin_real': finReal!.toIso8601String().substring(0, 10),
        if (diasRetraso != null) 'dias_retraso': diasRetraso!,
      };
}

class FaseEntrada {
  final String fase;
  final int orden;
  final int? diasEstimados;
  final bool? porValidar;

  const FaseEntrada({
    required this.fase,
    required this.orden,
    this.diasEstimados,
    this.porValidar,
  });

  factory FaseEntrada.fromJson(Map<String, dynamic> json) => FaseEntrada(
        fase: json['fase'] as String,
        orden: json['orden'] as int,
        diasEstimados: json['dias_estimados'] == null ? null : json['dias_estimados'] as int,
        porValidar: json['por_validar'] == null ? null : json['por_validar'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'fase': fase,
        'orden': orden,
        if (diasEstimados != null) 'dias_estimados': diasEstimados!,
        if (porValidar != null) 'por_validar': porValidar!,
      };
}

class FaseSalida {
  final String fase;
  final int orden;
  final int? diasEstimados;
  final bool porValidar;

  const FaseSalida({
    required this.fase,
    required this.orden,
    this.diasEstimados,
    required this.porValidar,
  });

  factory FaseSalida.fromJson(Map<String, dynamic> json) => FaseSalida(
        fase: json['fase'] as String,
        orden: json['orden'] as int,
        diasEstimados: json['dias_estimados'] == null ? null : json['dias_estimados'] as int,
        porValidar: json['por_validar'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'fase': fase,
        'orden': orden,
        if (diasEstimados != null) 'dias_estimados': diasEstimados!,
        'por_validar': porValidar,
      };
}

class FincaCreate {
  final String nombre;
  final String? ubicacion;
  final String? departamentoDane;
  final String? municipioDane;
  final double? areaHa;

  const FincaCreate({
    required this.nombre,
    this.ubicacion,
    this.departamentoDane,
    this.municipioDane,
    this.areaHa,
  });

  factory FincaCreate.fromJson(Map<String, dynamic> json) => FincaCreate(
        nombre: json['nombre'] as String,
        ubicacion: json['ubicacion'] == null ? null : json['ubicacion'] as String,
        departamentoDane: json['departamento_dane'] == null ? null : json['departamento_dane'] as String,
        municipioDane: json['municipio_dane'] == null ? null : json['municipio_dane'] as String,
        areaHa: json['area_ha'] == null ? null : (json['area_ha'] as num).toDouble(),
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        if (ubicacion != null) 'ubicacion': ubicacion!,
        if (departamentoDane != null) 'departamento_dane': departamentoDane!,
        if (municipioDane != null) 'municipio_dane': municipioDane!,
        if (areaHa != null) 'area_ha': areaHa!,
      };
}

class FincaResponse {
  final String id;
  final String nombre;
  final String? departamentoDane;
  final String? municipioDane;
  final String? areaHa;

  const FincaResponse({
    required this.id,
    required this.nombre,
    this.departamentoDane,
    this.municipioDane,
    this.areaHa,
  });

  factory FincaResponse.fromJson(Map<String, dynamic> json) => FincaResponse(
        id: json['id'] as String,
        nombre: json['nombre'] as String,
        departamentoDane: json['departamento_dane'] == null ? null : json['departamento_dane'] as String,
        municipioDane: json['municipio_dane'] == null ? null : json['municipio_dane'] as String,
        areaHa: json['area_ha'] == null ? null : json['area_ha'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'nombre': nombre,
        if (departamentoDane != null) 'departamento_dane': departamentoDane!,
        if (municipioDane != null) 'municipio_dane': municipioDane!,
        if (areaHa != null) 'area_ha': areaHa!,
      };
}

class FlujoCajaResponse {
  final String fincaId;
  final String? cicloId;
  final int anio;
  final int mes;
  final String ingresos;
  final String gastos;
  final String saldo;

  const FlujoCajaResponse({
    required this.fincaId,
    this.cicloId,
    required this.anio,
    required this.mes,
    required this.ingresos,
    required this.gastos,
    required this.saldo,
  });

  factory FlujoCajaResponse.fromJson(Map<String, dynamic> json) => FlujoCajaResponse(
        fincaId: json['finca_id'] as String,
        cicloId: json['ciclo_id'] == null ? null : json['ciclo_id'] as String,
        anio: json['anio'] as int,
        mes: json['mes'] as int,
        ingresos: json['ingresos'] as String,
        gastos: json['gastos'] as String,
        saldo: json['saldo'] as String,
      );

  Map<String, dynamic> toJson() => {
        'finca_id': fincaId,
        if (cicloId != null) 'ciclo_id': cicloId!,
        'anio': anio,
        'mes': mes,
        'ingresos': ingresos,
        'gastos': gastos,
        'saldo': saldo,
      };
}

class FuenteCrear {
  final String nombre;
  final String? url;
  final DateTime? fecha;
  final String? licencia;

  const FuenteCrear({
    required this.nombre,
    this.url,
    this.fecha,
    this.licencia,
  });

  factory FuenteCrear.fromJson(Map<String, dynamic> json) => FuenteCrear(
        nombre: json['nombre'] as String,
        url: json['url'] == null ? null : json['url'] as String,
        fecha: json['fecha'] == null ? null : DateTime.parse(json['fecha'] as String),
        licencia: json['licencia'] == null ? null : json['licencia'] as String,
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        if (url != null) 'url': url!,
        if (fecha != null) 'fecha': fecha!.toIso8601String().substring(0, 10),
        if (licencia != null) 'licencia': licencia!,
      };
}

class FuenteCreate {
  final String nombre;
  final String url;

  const FuenteCreate({
    required this.nombre,
    required this.url,
  });

  factory FuenteCreate.fromJson(Map<String, dynamic> json) => FuenteCreate(
        nombre: json['nombre'] as String,
        url: json['url'] as String,
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        'url': url,
      };
}

class FuenteSalida {
  final String id;
  final String nombre;
  final String? url;
  final DateTime? fecha;
  final String? licencia;

  const FuenteSalida({
    required this.id,
    required this.nombre,
    this.url,
    this.fecha,
    this.licencia,
  });

  factory FuenteSalida.fromJson(Map<String, dynamic> json) => FuenteSalida(
        id: json['id'] as String,
        nombre: json['nombre'] as String,
        url: json['url'] == null ? null : json['url'] as String,
        fecha: json['fecha'] == null ? null : DateTime.parse(json['fecha'] as String),
        licencia: json['licencia'] == null ? null : json['licencia'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'nombre': nombre,
        if (url != null) 'url': url!,
        if (fecha != null) 'fecha': fecha!.toIso8601String().substring(0, 10),
        if (licencia != null) 'licencia': licencia!,
      };
}

class GastoCreate {
  final String categoria;
  final double monto;
  final DateTime fecha;
  final String? cicloId;

  const GastoCreate({
    required this.categoria,
    required this.monto,
    required this.fecha,
    this.cicloId,
  });

  factory GastoCreate.fromJson(Map<String, dynamic> json) => GastoCreate(
        categoria: json['categoria'] as String,
        monto: (json['monto'] as num).toDouble(),
        fecha: DateTime.parse(json['fecha'] as String),
        cicloId: json['ciclo_id'] == null ? null : json['ciclo_id'] as String,
      );

  Map<String, dynamic> toJson() => {
        'categoria': categoria,
        'monto': monto,
        'fecha': fecha.toUtc().toIso8601String(),
        if (cicloId != null) 'ciclo_id': cicloId!,
      };
}

class HealthResponse {
  final String status;
  final String service;
  final String version;

  const HealthResponse({
    required this.status,
    required this.service,
    required this.version,
  });

  factory HealthResponse.fromJson(Map<String, dynamic> json) => HealthResponse(
        status: json['status'] as String,
        service: json['service'] as String,
        version: json['version'] as String,
      );

  Map<String, dynamic> toJson() => {
        'status': status,
        'service': service,
        'version': version,
      };
}

class Indicador {
  final String titulo;
  final double? valor;
  final String unidad;
  final String explicacion;
  final String estado;
  final String? queHacer;
  final DateTime? fechaDatos;

  const Indicador({
    required this.titulo,
    this.valor,
    required this.unidad,
    required this.explicacion,
    required this.estado,
    this.queHacer,
    this.fechaDatos,
  });

  factory Indicador.fromJson(Map<String, dynamic> json) => Indicador(
        titulo: json['titulo'] as String,
        valor: json['valor'] == null ? null : (json['valor'] as num).toDouble(),
        unidad: json['unidad'] as String,
        explicacion: json['explicacion'] as String,
        estado: json['estado'] as String,
        queHacer: json['que_hacer'] == null ? null : json['que_hacer'] as String,
        fechaDatos: json['fecha_datos'] == null ? null : DateTime.parse(json['fecha_datos'] as String),
      );

  Map<String, dynamic> toJson() => {
        'titulo': titulo,
        if (valor != null) 'valor': valor!,
        'unidad': unidad,
        'explicacion': explicacion,
        'estado': estado,
        if (queHacer != null) 'que_hacer': queHacer!,
        if (fechaDatos != null) 'fecha_datos': fechaDatos!.toIso8601String().substring(0, 10),
      };
}

class IndiceSiembra {
  final String siembraId;
  final String cultivo;
  final String loteId;
  final DateTime? fechaConteo;
  final List<Indicador> indicadores;
  final String? aviso;

  const IndiceSiembra({
    required this.siembraId,
    required this.cultivo,
    required this.loteId,
    this.fechaConteo,
    required this.indicadores,
    this.aviso,
  });

  factory IndiceSiembra.fromJson(Map<String, dynamic> json) => IndiceSiembra(
        siembraId: json['siembra_id'] as String,
        cultivo: json['cultivo'] as String,
        loteId: json['lote_id'] as String,
        fechaConteo: json['fecha_conteo'] == null ? null : DateTime.parse(json['fecha_conteo'] as String),
        indicadores: (json['indicadores'] as List<dynamic>).map((x) => Indicador.fromJson(x as Map<String, dynamic>)).toList(),
        aviso: json['aviso'] == null ? null : json['aviso'] as String,
      );

  Map<String, dynamic> toJson() => {
        'siembra_id': siembraId,
        'cultivo': cultivo,
        'lote_id': loteId,
        if (fechaConteo != null) 'fecha_conteo': fechaConteo!.toIso8601String().substring(0, 10),
        'indicadores': indicadores.map((x) => x.toJson()).toList(),
        if (aviso != null) 'aviso': aviso!,
      };
}

class IndicesSalida {
  final String siembraId;
  final DateTime? fechaConteo;
  final List<Indicador> indicadores;
  final String? aviso;

  const IndicesSalida({
    required this.siembraId,
    this.fechaConteo,
    required this.indicadores,
    this.aviso,
  });

  factory IndicesSalida.fromJson(Map<String, dynamic> json) => IndicesSalida(
        siembraId: json['siembra_id'] as String,
        fechaConteo: json['fecha_conteo'] == null ? null : DateTime.parse(json['fecha_conteo'] as String),
        indicadores: (json['indicadores'] as List<dynamic>).map((x) => Indicador.fromJson(x as Map<String, dynamic>)).toList(),
        aviso: json['aviso'] == null ? null : json['aviso'] as String,
      );

  Map<String, dynamic> toJson() => {
        'siembra_id': siembraId,
        if (fechaConteo != null) 'fecha_conteo': fechaConteo!.toIso8601String().substring(0, 10),
        'indicadores': indicadores.map((x) => x.toJson()).toList(),
        if (aviso != null) 'aviso': aviso!,
      };
}

class IngresoCreate {
  final String categoria;
  final double cantidad;
  final double precioUnitario;
  final double? total;
  final DateTime fecha;
  final String? cicloId;
  final String? comprador;

  const IngresoCreate({
    required this.categoria,
    required this.cantidad,
    required this.precioUnitario,
    this.total,
    required this.fecha,
    this.cicloId,
    this.comprador,
  });

  factory IngresoCreate.fromJson(Map<String, dynamic> json) => IngresoCreate(
        categoria: json['categoria'] as String,
        cantidad: (json['cantidad'] as num).toDouble(),
        precioUnitario: (json['precio_unitario'] as num).toDouble(),
        total: json['total'] == null ? null : (json['total'] as num).toDouble(),
        fecha: DateTime.parse(json['fecha'] as String),
        cicloId: json['ciclo_id'] == null ? null : json['ciclo_id'] as String,
        comprador: json['comprador'] == null ? null : json['comprador'] as String,
      );

  Map<String, dynamic> toJson() => {
        'categoria': categoria,
        'cantidad': cantidad,
        'precio_unitario': precioUnitario,
        if (total != null) 'total': total!,
        'fecha': fecha.toUtc().toIso8601String(),
        if (cicloId != null) 'ciclo_id': cicloId!,
        if (comprador != null) 'comprador': comprador!,
      };
}

class IniciarEntrada {
  final DateTime? fechaInicio;

  const IniciarEntrada({
    this.fechaInicio,
  });

  factory IniciarEntrada.fromJson(Map<String, dynamic> json) => IniciarEntrada(
        fechaInicio: json['fecha_inicio'] == null ? null : DateTime.parse(json['fecha_inicio'] as String),
      );

  Map<String, dynamic> toJson() => {
        if (fechaInicio != null) 'fecha_inicio': fechaInicio!.toIso8601String().substring(0, 10),
      };
}

class InicioSalida {
  final int fincas;
  final int siembrasEnCurso;
  final int siembrasPlaneadas;
  final List<AvisoRiesgo> avisos;
  final List<EventoReciente> eventosRecientes;
  final List<String> primerosPasos;

  const InicioSalida({
    required this.fincas,
    required this.siembrasEnCurso,
    required this.siembrasPlaneadas,
    required this.avisos,
    required this.eventosRecientes,
    required this.primerosPasos,
  });

  factory InicioSalida.fromJson(Map<String, dynamic> json) => InicioSalida(
        fincas: json['fincas'] as int,
        siembrasEnCurso: json['siembras_en_curso'] as int,
        siembrasPlaneadas: json['siembras_planeadas'] as int,
        avisos: (json['avisos'] as List<dynamic>).map((x) => AvisoRiesgo.fromJson(x as Map<String, dynamic>)).toList(),
        eventosRecientes: (json['eventos_recientes'] as List<dynamic>).map((x) => EventoReciente.fromJson(x as Map<String, dynamic>)).toList(),
        primerosPasos: (json['primeros_pasos'] as List<dynamic>).map((x) => x as String).toList(),
      );

  Map<String, dynamic> toJson() => {
        'fincas': fincas,
        'siembras_en_curso': siembrasEnCurso,
        'siembras_planeadas': siembrasPlaneadas,
        'avisos': avisos.map((x) => x.toJson()).toList(),
        'eventos_recientes': eventosRecientes.map((x) => x.toJson()).toList(),
        'primeros_pasos': primerosPasos.map((x) => x).toList(),
      };
}

class InsumoCreate {
  final String nombre;
  final String unidad;

  const InsumoCreate({
    required this.nombre,
    required this.unidad,
  });

  factory InsumoCreate.fromJson(Map<String, dynamic> json) => InsumoCreate(
        nombre: json['nombre'] as String,
        unidad: json['unidad'] as String,
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        'unidad': unidad,
      };
}

class InsumoResponse {
  final String id;
  final String fincaId;
  final String nombre;
  final String unidad;
  final String existencia;
  final String estado;

  const InsumoResponse({
    required this.id,
    required this.fincaId,
    required this.nombre,
    required this.unidad,
    required this.existencia,
    required this.estado,
  });

  factory InsumoResponse.fromJson(Map<String, dynamic> json) => InsumoResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        nombre: json['nombre'] as String,
        unidad: json['unidad'] as String,
        existencia: json['existencia'] as String,
        estado: json['estado'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'nombre': nombre,
        'unidad': unidad,
        'existencia': existencia,
        'estado': estado,
      };
}

class JornalCreate {
  final String? trabajadorId;
  final String actividadId;
  final String cicloId;
  final DateTime fecha;
  final double obreros;
  final double dias;
  final double valorJornal;
  final String? modalidad;

  const JornalCreate({
    this.trabajadorId,
    required this.actividadId,
    required this.cicloId,
    required this.fecha,
    required this.obreros,
    required this.dias,
    required this.valorJornal,
    this.modalidad,
  });

  factory JornalCreate.fromJson(Map<String, dynamic> json) => JornalCreate(
        trabajadorId: json['trabajador_id'] == null ? null : json['trabajador_id'] as String,
        actividadId: json['actividad_id'] as String,
        cicloId: json['ciclo_id'] as String,
        fecha: DateTime.parse(json['fecha'] as String),
        obreros: (json['obreros'] as num).toDouble(),
        dias: (json['dias'] as num).toDouble(),
        valorJornal: (json['valor_jornal'] as num).toDouble(),
        modalidad: json['modalidad'] == null ? null : json['modalidad'] as String,
      );

  Map<String, dynamic> toJson() => {
        if (trabajadorId != null) 'trabajador_id': trabajadorId!,
        'actividad_id': actividadId,
        'ciclo_id': cicloId,
        'fecha': fecha.toUtc().toIso8601String(),
        'obreros': obreros,
        'dias': dias,
        'valor_jornal': valorJornal,
        if (modalidad != null) 'modalidad': modalidad!,
      };
}

class JornalResponse {
  final String id;
  final String fincaId;
  final String? trabajadorId;
  final String actividadId;
  final String cicloId;
  final DateTime fecha;
  final String obreros;
  final String dias;
  final String valorJornal;
  final String modalidad;
  final String total;
  final String estado;

  const JornalResponse({
    required this.id,
    required this.fincaId,
    this.trabajadorId,
    required this.actividadId,
    required this.cicloId,
    required this.fecha,
    required this.obreros,
    required this.dias,
    required this.valorJornal,
    required this.modalidad,
    required this.total,
    required this.estado,
  });

  factory JornalResponse.fromJson(Map<String, dynamic> json) => JornalResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        trabajadorId: json['trabajador_id'] == null ? null : json['trabajador_id'] as String,
        actividadId: json['actividad_id'] as String,
        cicloId: json['ciclo_id'] as String,
        fecha: DateTime.parse(json['fecha'] as String),
        obreros: json['obreros'] as String,
        dias: json['dias'] as String,
        valorJornal: json['valor_jornal'] as String,
        modalidad: json['modalidad'] as String,
        total: json['total'] as String,
        estado: json['estado'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        if (trabajadorId != null) 'trabajador_id': trabajadorId!,
        'actividad_id': actividadId,
        'ciclo_id': cicloId,
        'fecha': fecha.toUtc().toIso8601String(),
        'obreros': obreros,
        'dias': dias,
        'valor_jornal': valorJornal,
        'modalidad': modalidad,
        'total': total,
        'estado': estado,
      };
}

class LineaVentaCreate {
  final String cosechaId;
  final String categoria;
  final String unidad;
  final double cantidad;
  final double? merma;
  final double precioUnitario;

  const LineaVentaCreate({
    required this.cosechaId,
    required this.categoria,
    required this.unidad,
    required this.cantidad,
    this.merma,
    required this.precioUnitario,
  });

  factory LineaVentaCreate.fromJson(Map<String, dynamic> json) => LineaVentaCreate(
        cosechaId: json['cosecha_id'] as String,
        categoria: json['categoria'] as String,
        unidad: json['unidad'] as String,
        cantidad: (json['cantidad'] as num).toDouble(),
        merma: json['merma'] == null ? null : (json['merma'] as num).toDouble(),
        precioUnitario: (json['precio_unitario'] as num).toDouble(),
      );

  Map<String, dynamic> toJson() => {
        'cosecha_id': cosechaId,
        'categoria': categoria,
        'unidad': unidad,
        'cantidad': cantidad,
        if (merma != null) 'merma': merma!,
        'precio_unitario': precioUnitario,
      };
}

class LoginRequest {
  final String email;
  final String password;

  const LoginRequest({
    required this.email,
    required this.password,
  });

  factory LoginRequest.fromJson(Map<String, dynamic> json) => LoginRequest(
        email: json['email'] as String,
        password: json['password'] as String,
      );

  Map<String, dynamic> toJson() => {
        'email': email,
        'password': password,
      };
}

class LoteAnimalCreate {
  final String especieId;
  final String nombre;
  final double cantidad;
  final String? ubicacion;

  const LoteAnimalCreate({
    required this.especieId,
    required this.nombre,
    required this.cantidad,
    this.ubicacion,
  });

  factory LoteAnimalCreate.fromJson(Map<String, dynamic> json) => LoteAnimalCreate(
        especieId: json['especie_id'] as String,
        nombre: json['nombre'] as String,
        cantidad: (json['cantidad'] as num).toDouble(),
        ubicacion: json['ubicacion'] == null ? null : json['ubicacion'] as String,
      );

  Map<String, dynamic> toJson() => {
        'especie_id': especieId,
        'nombre': nombre,
        'cantidad': cantidad,
        if (ubicacion != null) 'ubicacion': ubicacion!,
      };
}

class LoteAnimalResponse {
  final String id;
  final String fincaId;
  final String especieId;
  final String nombre;
  final String cantidad;
  final String? ubicacion;

  const LoteAnimalResponse({
    required this.id,
    required this.fincaId,
    required this.especieId,
    required this.nombre,
    required this.cantidad,
    this.ubicacion,
  });

  factory LoteAnimalResponse.fromJson(Map<String, dynamic> json) => LoteAnimalResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        especieId: json['especie_id'] as String,
        nombre: json['nombre'] as String,
        cantidad: json['cantidad'] as String,
        ubicacion: json['ubicacion'] == null ? null : json['ubicacion'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'especie_id': especieId,
        'nombre': nombre,
        'cantidad': cantidad,
        if (ubicacion != null) 'ubicacion': ubicacion!,
      };
}

class LoteCreate {
  final String nombre;
  final double area;
  final String? notas;

  const LoteCreate({
    required this.nombre,
    required this.area,
    this.notas,
  });

  factory LoteCreate.fromJson(Map<String, dynamic> json) => LoteCreate(
        nombre: json['nombre'] as String,
        area: (json['area'] as num).toDouble(),
        notas: json['notas'] == null ? null : json['notas'] as String,
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        'area': area,
        if (notas != null) 'notas': notas!,
      };
}

class LoteResponse {
  final String id;
  final String fincaId;
  final String nombre;
  final String area;
  final String? notas;

  const LoteResponse({
    required this.id,
    required this.fincaId,
    required this.nombre,
    required this.area,
    this.notas,
  });

  factory LoteResponse.fromJson(Map<String, dynamic> json) => LoteResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        nombre: json['nombre'] as String,
        area: json['area'] as String,
        notas: json['notas'] == null ? null : json['notas'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'nombre': nombre,
        'area': area,
        if (notas != null) 'notas': notas!,
      };
}

class ManejoEntrada {
  final String tipo;
  final String descripcion;
  final String? productoIca;
  final String? fuenteId;

  const ManejoEntrada({
    required this.tipo,
    required this.descripcion,
    this.productoIca,
    this.fuenteId,
  });

  factory ManejoEntrada.fromJson(Map<String, dynamic> json) => ManejoEntrada(
        tipo: json['tipo'] as String,
        descripcion: json['descripcion'] as String,
        productoIca: json['producto_ica'] == null ? null : json['producto_ica'] as String,
        fuenteId: json['fuente_id'] == null ? null : json['fuente_id'] as String,
      );

  Map<String, dynamic> toJson() => {
        'tipo': tipo,
        'descripcion': descripcion,
        if (productoIca != null) 'producto_ica': productoIca!,
        if (fuenteId != null) 'fuente_id': fuenteId!,
      };
}

class ManejoSalida {
  final String tipo;
  final String descripcion;
  final String? productoIca;
  final FuenteSalida? fuente;

  const ManejoSalida({
    required this.tipo,
    required this.descripcion,
    this.productoIca,
    this.fuente,
  });

  factory ManejoSalida.fromJson(Map<String, dynamic> json) => ManejoSalida(
        tipo: json['tipo'] as String,
        descripcion: json['descripcion'] as String,
        productoIca: json['producto_ica'] == null ? null : json['producto_ica'] as String,
        fuente: json['fuente'] == null ? null : FuenteSalida.fromJson(json['fuente'] as Map<String, dynamic>),
      );

  Map<String, dynamic> toJson() => {
        'tipo': tipo,
        'descripcion': descripcion,
        if (productoIca != null) 'producto_ica': productoIca!,
        if (fuente != null) 'fuente': fuente!.toJson(),
      };
}

class MetodoEntrada {
  final String metodo;
  final int? diasGerminacion;
  final int? diasVivero;
  final bool? porValidar;

  const MetodoEntrada({
    required this.metodo,
    this.diasGerminacion,
    this.diasVivero,
    this.porValidar,
  });

  factory MetodoEntrada.fromJson(Map<String, dynamic> json) => MetodoEntrada(
        metodo: json['metodo'] as String,
        diasGerminacion: json['dias_germinacion'] == null ? null : json['dias_germinacion'] as int,
        diasVivero: json['dias_vivero'] == null ? null : json['dias_vivero'] as int,
        porValidar: json['por_validar'] == null ? null : json['por_validar'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'metodo': metodo,
        if (diasGerminacion != null) 'dias_germinacion': diasGerminacion!,
        if (diasVivero != null) 'dias_vivero': diasVivero!,
        if (porValidar != null) 'por_validar': porValidar!,
      };
}

class MetodoSalida {
  final String metodo;
  final int? diasGerminacion;
  final int? diasVivero;
  final bool porValidar;

  const MetodoSalida({
    required this.metodo,
    this.diasGerminacion,
    this.diasVivero,
    required this.porValidar,
  });

  factory MetodoSalida.fromJson(Map<String, dynamic> json) => MetodoSalida(
        metodo: json['metodo'] as String,
        diasGerminacion: json['dias_germinacion'] == null ? null : json['dias_germinacion'] as int,
        diasVivero: json['dias_vivero'] == null ? null : json['dias_vivero'] as int,
        porValidar: json['por_validar'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'metodo': metodo,
        if (diasGerminacion != null) 'dias_germinacion': diasGerminacion!,
        if (diasVivero != null) 'dias_vivero': diasVivero!,
        'por_validar': porValidar,
      };
}

class MovimientoCreate {
  final String insumoId;
  final double cantidad;
  final DateTime fecha;
  final double? costo;
  final String? actividadId;

  const MovimientoCreate({
    required this.insumoId,
    required this.cantidad,
    required this.fecha,
    this.costo,
    this.actividadId,
  });

  factory MovimientoCreate.fromJson(Map<String, dynamic> json) => MovimientoCreate(
        insumoId: json['insumo_id'] as String,
        cantidad: (json['cantidad'] as num).toDouble(),
        fecha: DateTime.parse(json['fecha'] as String),
        costo: json['costo'] == null ? null : (json['costo'] as num).toDouble(),
        actividadId: json['actividad_id'] == null ? null : json['actividad_id'] as String,
      );

  Map<String, dynamic> toJson() => {
        'insumo_id': insumoId,
        'cantidad': cantidad,
        'fecha': fecha.toUtc().toIso8601String(),
        if (costo != null) 'costo': costo!,
        if (actividadId != null) 'actividad_id': actividadId!,
      };
}

class MovimientoResponse {
  final String id;
  final String fincaId;
  final String insumoId;
  final String? actividadId;
  final String tipo;
  final String cantidad;
  final String costo;
  final DateTime fecha;
  final String creadoPor;

  const MovimientoResponse({
    required this.id,
    required this.fincaId,
    required this.insumoId,
    this.actividadId,
    required this.tipo,
    required this.cantidad,
    required this.costo,
    required this.fecha,
    required this.creadoPor,
  });

  factory MovimientoResponse.fromJson(Map<String, dynamic> json) => MovimientoResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        insumoId: json['insumo_id'] as String,
        actividadId: json['actividad_id'] == null ? null : json['actividad_id'] as String,
        tipo: json['tipo'] as String,
        cantidad: json['cantidad'] as String,
        costo: json['costo'] as String,
        fecha: DateTime.parse(json['fecha'] as String),
        creadoPor: json['creado_por'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'insumo_id': insumoId,
        if (actividadId != null) 'actividad_id': actividadId!,
        'tipo': tipo,
        'cantidad': cantidad,
        'costo': costo,
        'fecha': fecha.toUtc().toIso8601String(),
        'creado_por': creadoPor,
      };
}

class NecesidadItem {
  final String insumoTipo;
  final double dosis;
  final String unidad;
  final String base;
  final double? cantidadNecesaria;
  final bool porValidar;
  final String? mensaje;

  const NecesidadItem({
    required this.insumoTipo,
    required this.dosis,
    required this.unidad,
    required this.base,
    this.cantidadNecesaria,
    required this.porValidar,
    this.mensaje,
  });

  factory NecesidadItem.fromJson(Map<String, dynamic> json) => NecesidadItem(
        insumoTipo: json['insumo_tipo'] as String,
        dosis: (json['dosis'] as num).toDouble(),
        unidad: json['unidad'] as String,
        base: json['base'] as String,
        cantidadNecesaria: json['cantidad_necesaria'] == null ? null : (json['cantidad_necesaria'] as num).toDouble(),
        porValidar: json['por_validar'] as bool,
        mensaje: json['mensaje'] == null ? null : json['mensaje'] as String,
      );

  Map<String, dynamic> toJson() => {
        'insumo_tipo': insumoTipo,
        'dosis': dosis,
        'unidad': unidad,
        'base': base,
        if (cantidadNecesaria != null) 'cantidad_necesaria': cantidadNecesaria!,
        'por_validar': porValidar,
        if (mensaje != null) 'mensaje': mensaje!,
      };
}

class NecesidadSalida {
  final String cicloId;
  final List<NecesidadItem> items;
  final String? aviso;

  const NecesidadSalida({
    required this.cicloId,
    required this.items,
    this.aviso,
  });

  factory NecesidadSalida.fromJson(Map<String, dynamic> json) => NecesidadSalida(
        cicloId: json['ciclo_id'] as String,
        items: (json['items'] as List<dynamic>).map((x) => NecesidadItem.fromJson(x as Map<String, dynamic>)).toList(),
        aviso: json['aviso'] == null ? null : json['aviso'] as String,
      );

  Map<String, dynamic> toJson() => {
        'ciclo_id': cicloId,
        'items': items.map((x) => x.toJson()).toList(),
        if (aviso != null) 'aviso': aviso!,
      };
}

class NoticiaCrear {
  final String titulo;
  final String resumen;
  final String enlace;
  final String fuente;
  final String? regionDane;
  final String? cultivoId;
  final DateTime? publicada;
  final DateTime? vigenteHasta;

  const NoticiaCrear({
    required this.titulo,
    required this.resumen,
    required this.enlace,
    required this.fuente,
    this.regionDane,
    this.cultivoId,
    this.publicada,
    this.vigenteHasta,
  });

  factory NoticiaCrear.fromJson(Map<String, dynamic> json) => NoticiaCrear(
        titulo: json['titulo'] as String,
        resumen: json['resumen'] as String,
        enlace: json['enlace'] as String,
        fuente: json['fuente'] as String,
        regionDane: json['region_dane'] == null ? null : json['region_dane'] as String,
        cultivoId: json['cultivo_id'] == null ? null : json['cultivo_id'] as String,
        publicada: json['publicada'] == null ? null : DateTime.parse(json['publicada'] as String),
        vigenteHasta: json['vigente_hasta'] == null ? null : DateTime.parse(json['vigente_hasta'] as String),
      );

  Map<String, dynamic> toJson() => {
        'titulo': titulo,
        'resumen': resumen,
        'enlace': enlace,
        'fuente': fuente,
        if (regionDane != null) 'region_dane': regionDane!,
        if (cultivoId != null) 'cultivo_id': cultivoId!,
        if (publicada != null) 'publicada': publicada!.toUtc().toIso8601String(),
        if (vigenteHasta != null) 'vigente_hasta': vigenteHasta!.toUtc().toIso8601String(),
      };
}

class NoticiaSalida {
  final String id;
  final String titulo;
  final String resumen;
  final String enlace;
  final String fuente;
  final String? regionDane;
  final String? cultivoId;
  final DateTime publicada;
  final DateTime vigenteHasta;

  const NoticiaSalida({
    required this.id,
    required this.titulo,
    required this.resumen,
    required this.enlace,
    required this.fuente,
    this.regionDane,
    this.cultivoId,
    required this.publicada,
    required this.vigenteHasta,
  });

  factory NoticiaSalida.fromJson(Map<String, dynamic> json) => NoticiaSalida(
        id: json['id'] as String,
        titulo: json['titulo'] as String,
        resumen: json['resumen'] as String,
        enlace: json['enlace'] as String,
        fuente: json['fuente'] as String,
        regionDane: json['region_dane'] == null ? null : json['region_dane'] as String,
        cultivoId: json['cultivo_id'] == null ? null : json['cultivo_id'] as String,
        publicada: DateTime.parse(json['publicada'] as String),
        vigenteHasta: DateTime.parse(json['vigente_hasta'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'titulo': titulo,
        'resumen': resumen,
        'enlace': enlace,
        'fuente': fuente,
        if (regionDane != null) 'region_dane': regionDane!,
        if (cultivoId != null) 'cultivo_id': cultivoId!,
        'publicada': publicada.toUtc().toIso8601String(),
        'vigente_hasta': vigenteHasta.toUtc().toIso8601String(),
      };
}

class PageConsultaResumen {
  final List<ConsultaResumen> items;
  final int total;
  final int page;
  final int size;
  final bool hasMore;

  const PageConsultaResumen({
    required this.items,
    required this.total,
    required this.page,
    required this.size,
    required this.hasMore,
  });

  factory PageConsultaResumen.fromJson(Map<String, dynamic> json) => PageConsultaResumen(
        items: (json['items'] as List<dynamic>).map((x) => ConsultaResumen.fromJson(x as Map<String, dynamic>)).toList(),
        total: json['total'] as int,
        page: json['page'] as int,
        size: json['size'] as int,
        hasMore: json['has_more'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'items': items.map((x) => x.toJson()).toList(),
        'total': total,
        'page': page,
        'size': size,
        'has_more': hasMore,
      };
}

class PageCultivoResumen {
  final List<CultivoResumen> items;
  final int total;
  final int page;
  final int size;
  final bool hasMore;

  const PageCultivoResumen({
    required this.items,
    required this.total,
    required this.page,
    required this.size,
    required this.hasMore,
  });

  factory PageCultivoResumen.fromJson(Map<String, dynamic> json) => PageCultivoResumen(
        items: (json['items'] as List<dynamic>).map((x) => CultivoResumen.fromJson(x as Map<String, dynamic>)).toList(),
        total: json['total'] as int,
        page: json['page'] as int,
        size: json['size'] as int,
        hasMore: json['has_more'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'items': items.map((x) => x.toJson()).toList(),
        'total': total,
        'page': page,
        'size': size,
        'has_more': hasMore,
      };
}

class PageEventoSalida {
  final List<EventoSalida> items;
  final int total;
  final int page;
  final int size;
  final bool hasMore;

  const PageEventoSalida({
    required this.items,
    required this.total,
    required this.page,
    required this.size,
    required this.hasMore,
  });

  factory PageEventoSalida.fromJson(Map<String, dynamic> json) => PageEventoSalida(
        items: (json['items'] as List<dynamic>).map((x) => EventoSalida.fromJson(x as Map<String, dynamic>)).toList(),
        total: json['total'] as int,
        page: json['page'] as int,
        size: json['size'] as int,
        hasMore: json['has_more'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'items': items.map((x) => x.toJson()).toList(),
        'total': total,
        'page': page,
        'size': size,
        'has_more': hasMore,
      };
}

class PageNoticiaSalida {
  final List<NoticiaSalida> items;
  final int total;
  final int page;
  final int size;
  final bool hasMore;

  const PageNoticiaSalida({
    required this.items,
    required this.total,
    required this.page,
    required this.size,
    required this.hasMore,
  });

  factory PageNoticiaSalida.fromJson(Map<String, dynamic> json) => PageNoticiaSalida(
        items: (json['items'] as List<dynamic>).map((x) => NoticiaSalida.fromJson(x as Map<String, dynamic>)).toList(),
        total: json['total'] as int,
        page: json['page'] as int,
        size: json['size'] as int,
        hasMore: json['has_more'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'items': items.map((x) => x.toJson()).toList(),
        'total': total,
        'page': page,
        'size': size,
        'has_more': hasMore,
      };
}

class PageProblemaResumen {
  final List<ProblemaResumen> items;
  final int total;
  final int page;
  final int size;
  final bool hasMore;

  const PageProblemaResumen({
    required this.items,
    required this.total,
    required this.page,
    required this.size,
    required this.hasMore,
  });

  factory PageProblemaResumen.fromJson(Map<String, dynamic> json) => PageProblemaResumen(
        items: (json['items'] as List<dynamic>).map((x) => ProblemaResumen.fromJson(x as Map<String, dynamic>)).toList(),
        total: json['total'] as int,
        page: json['page'] as int,
        size: json['size'] as int,
        hasMore: json['has_more'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'items': items.map((x) => x.toJson()).toList(),
        'total': total,
        'page': page,
        'size': size,
        'has_more': hasMore,
      };
}

class PagePropagacionSalida {
  final List<PropagacionSalida> items;
  final int total;
  final int page;
  final int size;
  final bool hasMore;

  const PagePropagacionSalida({
    required this.items,
    required this.total,
    required this.page,
    required this.size,
    required this.hasMore,
  });

  factory PagePropagacionSalida.fromJson(Map<String, dynamic> json) => PagePropagacionSalida(
        items: (json['items'] as List<dynamic>).map((x) => PropagacionSalida.fromJson(x as Map<String, dynamic>)).toList(),
        total: json['total'] as int,
        page: json['page'] as int,
        size: json['size'] as int,
        hasMore: json['has_more'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'items': items.map((x) => x.toJson()).toList(),
        'total': total,
        'page': page,
        'size': size,
        'has_more': hasMore,
      };
}

class PageSiembraResumen {
  final List<SiembraResumen> items;
  final int total;
  final int page;
  final int size;
  final bool hasMore;

  const PageSiembraResumen({
    required this.items,
    required this.total,
    required this.page,
    required this.size,
    required this.hasMore,
  });

  factory PageSiembraResumen.fromJson(Map<String, dynamic> json) => PageSiembraResumen(
        items: (json['items'] as List<dynamic>).map((x) => SiembraResumen.fromJson(x as Map<String, dynamic>)).toList(),
        total: json['total'] as int,
        page: json['page'] as int,
        size: json['size'] as int,
        hasMore: json['has_more'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'items': items.map((x) => x.toJson()).toList(),
        'total': total,
        'page': page,
        'size': size,
        'has_more': hasMore,
      };
}

class PerfilResponse {
  final String id;
  final String email;
  final String nombre;
  final String rol;
  final bool activo;
  final List<String> fincas;
  final List<PermisoResponse> permisos;

  const PerfilResponse({
    required this.id,
    required this.email,
    required this.nombre,
    required this.rol,
    required this.activo,
    required this.fincas,
    required this.permisos,
  });

  factory PerfilResponse.fromJson(Map<String, dynamic> json) => PerfilResponse(
        id: json['id'] as String,
        email: json['email'] as String,
        nombre: json['nombre'] as String,
        rol: json['rol'] as String,
        activo: json['activo'] as bool,
        fincas: (json['fincas'] as List<dynamic>).map((x) => x as String).toList(),
        permisos: (json['permisos'] as List<dynamic>).map((x) => PermisoResponse.fromJson(x as Map<String, dynamic>)).toList(),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'nombre': nombre,
        'rol': rol,
        'activo': activo,
        'fincas': fincas.map((x) => x).toList(),
        'permisos': permisos.map((x) => x.toJson()).toList(),
      };
}

class PermisoResponse {
  final String grupo;
  final String metodo;
  final String ruta;
  final String resumen;

  const PermisoResponse({
    required this.grupo,
    required this.metodo,
    required this.ruta,
    required this.resumen,
  });

  factory PermisoResponse.fromJson(Map<String, dynamic> json) => PermisoResponse(
        grupo: json['grupo'] as String,
        metodo: json['metodo'] as String,
        ruta: json['ruta'] as String,
        resumen: json['resumen'] as String,
      );

  Map<String, dynamic> toJson() => {
        'grupo': grupo,
        'metodo': metodo,
        'ruta': ruta,
        'resumen': resumen,
      };
}

class PoliticaSalida {
  final String version;
  final String estado;
  final List<String> datosQueUsamos;
  final List<String> paraQue;
  final List<String> susDerechos;

  const PoliticaSalida({
    required this.version,
    required this.estado,
    required this.datosQueUsamos,
    required this.paraQue,
    required this.susDerechos,
  });

  factory PoliticaSalida.fromJson(Map<String, dynamic> json) => PoliticaSalida(
        version: json['version'] as String,
        estado: json['estado'] as String,
        datosQueUsamos: (json['datos_que_usamos'] as List<dynamic>).map((x) => x as String).toList(),
        paraQue: (json['para_que'] as List<dynamic>).map((x) => x as String).toList(),
        susDerechos: (json['sus_derechos'] as List<dynamic>).map((x) => x as String).toList(),
      );

  Map<String, dynamic> toJson() => {
        'version': version,
        'estado': estado,
        'datos_que_usamos': datosQueUsamos.map((x) => x).toList(),
        'para_que': paraQue.map((x) => x).toList(),
        'sus_derechos': susDerechos.map((x) => x).toList(),
      };
}

class PrecioCreate {
  final String categoria;
  final String unidad;
  final double precio;
  final DateTime vigenteDesde;
  final DateTime? vigenteHasta;

  const PrecioCreate({
    required this.categoria,
    required this.unidad,
    required this.precio,
    required this.vigenteDesde,
    this.vigenteHasta,
  });

  factory PrecioCreate.fromJson(Map<String, dynamic> json) => PrecioCreate(
        categoria: json['categoria'] as String,
        unidad: json['unidad'] as String,
        precio: (json['precio'] as num).toDouble(),
        vigenteDesde: DateTime.parse(json['vigente_desde'] as String),
        vigenteHasta: json['vigente_hasta'] == null ? null : DateTime.parse(json['vigente_hasta'] as String),
      );

  Map<String, dynamic> toJson() => {
        'categoria': categoria,
        'unidad': unidad,
        'precio': precio,
        'vigente_desde': vigenteDesde.toUtc().toIso8601String(),
        if (vigenteHasta != null) 'vigente_hasta': vigenteHasta!.toUtc().toIso8601String(),
      };
}

class PrecioResponse {
  final String id;
  final String fincaId;
  final String categoria;
  final String unidad;
  final String precio;
  final DateTime vigenteDesde;
  final DateTime? vigenteHasta;

  const PrecioResponse({
    required this.id,
    required this.fincaId,
    required this.categoria,
    required this.unidad,
    required this.precio,
    required this.vigenteDesde,
    this.vigenteHasta,
  });

  factory PrecioResponse.fromJson(Map<String, dynamic> json) => PrecioResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        categoria: json['categoria'] as String,
        unidad: json['unidad'] as String,
        precio: json['precio'] as String,
        vigenteDesde: DateTime.parse(json['vigente_desde'] as String),
        vigenteHasta: json['vigente_hasta'] == null ? null : DateTime.parse(json['vigente_hasta'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'categoria': categoria,
        'unidad': unidad,
        'precio': precio,
        'vigente_desde': vigenteDesde.toUtc().toIso8601String(),
        if (vigenteHasta != null) 'vigente_hasta': vigenteHasta!.toUtc().toIso8601String(),
      };
}

class ProblemaCrear {
  final String nombre;
  final String tipo;
  final String? cultivoId;
  final String? causa;
  final List<SintomaEntrada>? sintomas;
  final List<ManejoEntrada>? manejos;

  const ProblemaCrear({
    required this.nombre,
    required this.tipo,
    this.cultivoId,
    this.causa,
    this.sintomas,
    this.manejos,
  });

  factory ProblemaCrear.fromJson(Map<String, dynamic> json) => ProblemaCrear(
        nombre: json['nombre'] as String,
        tipo: json['tipo'] as String,
        cultivoId: json['cultivo_id'] == null ? null : json['cultivo_id'] as String,
        causa: json['causa'] == null ? null : json['causa'] as String,
        sintomas: json['sintomas'] == null ? null : (json['sintomas'] as List<dynamic>).map((x) => SintomaEntrada.fromJson(x as Map<String, dynamic>)).toList(),
        manejos: json['manejos'] == null ? null : (json['manejos'] as List<dynamic>).map((x) => ManejoEntrada.fromJson(x as Map<String, dynamic>)).toList(),
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        'tipo': tipo,
        if (cultivoId != null) 'cultivo_id': cultivoId!,
        if (causa != null) 'causa': causa!,
        if (sintomas != null) 'sintomas': sintomas!.map((x) => x.toJson()).toList(),
        if (manejos != null) 'manejos': manejos!.map((x) => x.toJson()).toList(),
      };
}

class ProblemaResumen {
  final String id;
  final String nombre;
  final String tipo;
  final String? cultivoId;
  final String estado;

  const ProblemaResumen({
    required this.id,
    required this.nombre,
    required this.tipo,
    this.cultivoId,
    required this.estado,
  });

  factory ProblemaResumen.fromJson(Map<String, dynamic> json) => ProblemaResumen(
        id: json['id'] as String,
        nombre: json['nombre'] as String,
        tipo: json['tipo'] as String,
        cultivoId: json['cultivo_id'] == null ? null : json['cultivo_id'] as String,
        estado: json['estado'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'nombre': nombre,
        'tipo': tipo,
        if (cultivoId != null) 'cultivo_id': cultivoId!,
        'estado': estado,
      };
}

class ProblemaRevision {
  final String id;
  final String nombre;
  final String tipo;
  final String? cultivoId;
  final String estado;
  final String? causa;
  final List<SintomaSalida> sintomas;
  final List<ManejoSalida> manejos;
  final String? aviso;
  final List<ValidacionSalida> validaciones;

  const ProblemaRevision({
    required this.id,
    required this.nombre,
    required this.tipo,
    this.cultivoId,
    required this.estado,
    this.causa,
    required this.sintomas,
    required this.manejos,
    this.aviso,
    required this.validaciones,
  });

  factory ProblemaRevision.fromJson(Map<String, dynamic> json) => ProblemaRevision(
        id: json['id'] as String,
        nombre: json['nombre'] as String,
        tipo: json['tipo'] as String,
        cultivoId: json['cultivo_id'] == null ? null : json['cultivo_id'] as String,
        estado: json['estado'] as String,
        causa: json['causa'] == null ? null : json['causa'] as String,
        sintomas: (json['sintomas'] as List<dynamic>).map((x) => SintomaSalida.fromJson(x as Map<String, dynamic>)).toList(),
        manejos: (json['manejos'] as List<dynamic>).map((x) => ManejoSalida.fromJson(x as Map<String, dynamic>)).toList(),
        aviso: json['aviso'] == null ? null : json['aviso'] as String,
        validaciones: (json['validaciones'] as List<dynamic>).map((x) => ValidacionSalida.fromJson(x as Map<String, dynamic>)).toList(),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'nombre': nombre,
        'tipo': tipo,
        if (cultivoId != null) 'cultivo_id': cultivoId!,
        'estado': estado,
        if (causa != null) 'causa': causa!,
        'sintomas': sintomas.map((x) => x.toJson()).toList(),
        'manejos': manejos.map((x) => x.toJson()).toList(),
        if (aviso != null) 'aviso': aviso!,
        'validaciones': validaciones.map((x) => x.toJson()).toList(),
      };
}

class ProcesoCreate {
  final String nombre;
  final String producto;
  final String materiaPrima;
  final String origenMateria;
  final DateTime fechaInicio;

  const ProcesoCreate({
    required this.nombre,
    required this.producto,
    required this.materiaPrima,
    required this.origenMateria,
    required this.fechaInicio,
  });

  factory ProcesoCreate.fromJson(Map<String, dynamic> json) => ProcesoCreate(
        nombre: json['nombre'] as String,
        producto: json['producto'] as String,
        materiaPrima: json['materia_prima'] as String,
        origenMateria: json['origen_materia'] as String,
        fechaInicio: DateTime.parse(json['fecha_inicio'] as String),
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        'producto': producto,
        'materia_prima': materiaPrima,
        'origen_materia': origenMateria,
        'fecha_inicio': fechaInicio.toUtc().toIso8601String(),
      };
}

class ProcesoResponse {
  final String id;
  final String fincaId;
  final String nombre;
  final String producto;
  final String materiaPrima;
  final String origenMateria;
  final DateTime fechaInicio;
  final DateTime? fechaFin;

  const ProcesoResponse({
    required this.id,
    required this.fincaId,
    required this.nombre,
    required this.producto,
    required this.materiaPrima,
    required this.origenMateria,
    required this.fechaInicio,
    this.fechaFin,
  });

  factory ProcesoResponse.fromJson(Map<String, dynamic> json) => ProcesoResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        nombre: json['nombre'] as String,
        producto: json['producto'] as String,
        materiaPrima: json['materia_prima'] as String,
        origenMateria: json['origen_materia'] as String,
        fechaInicio: DateTime.parse(json['fecha_inicio'] as String),
        fechaFin: json['fecha_fin'] == null ? null : DateTime.parse(json['fecha_fin'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'nombre': nombre,
        'producto': producto,
        'materia_prima': materiaPrima,
        'origen_materia': origenMateria,
        'fecha_inicio': fechaInicio.toUtc().toIso8601String(),
        if (fechaFin != null) 'fecha_fin': fechaFin!.toUtc().toIso8601String(),
      };
}

class ProduccionCreate {
  final String loteAnimalId;
  final DateTime fecha;
  final String tipo;
  final double cantidad;
  final String unidad;

  const ProduccionCreate({
    required this.loteAnimalId,
    required this.fecha,
    required this.tipo,
    required this.cantidad,
    required this.unidad,
  });

  factory ProduccionCreate.fromJson(Map<String, dynamic> json) => ProduccionCreate(
        loteAnimalId: json['lote_animal_id'] as String,
        fecha: DateTime.parse(json['fecha'] as String),
        tipo: json['tipo'] as String,
        cantidad: (json['cantidad'] as num).toDouble(),
        unidad: json['unidad'] as String,
      );

  Map<String, dynamic> toJson() => {
        'lote_animal_id': loteAnimalId,
        'fecha': fecha.toUtc().toIso8601String(),
        'tipo': tipo,
        'cantidad': cantidad,
        'unidad': unidad,
      };
}

class ProduccionResponse {
  final String id;
  final String fincaId;
  final String loteAnimalId;
  final DateTime fecha;
  final String tipo;
  final String cantidad;
  final String unidad;

  const ProduccionResponse({
    required this.id,
    required this.fincaId,
    required this.loteAnimalId,
    required this.fecha,
    required this.tipo,
    required this.cantidad,
    required this.unidad,
  });

  factory ProduccionResponse.fromJson(Map<String, dynamic> json) => ProduccionResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        loteAnimalId: json['lote_animal_id'] as String,
        fecha: DateTime.parse(json['fecha'] as String),
        tipo: json['tipo'] as String,
        cantidad: json['cantidad'] as String,
        unidad: json['unidad'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'lote_animal_id': loteAnimalId,
        'fecha': fecha.toUtc().toIso8601String(),
        'tipo': tipo,
        'cantidad': cantidad,
        'unidad': unidad,
      };
}

class PropagacionActualizar {
  final int? germinadas;
  final int? listas;
  final int? perdidas;

  const PropagacionActualizar({
    this.germinadas,
    this.listas,
    this.perdidas,
  });

  factory PropagacionActualizar.fromJson(Map<String, dynamic> json) => PropagacionActualizar(
        germinadas: json['germinadas'] == null ? null : json['germinadas'] as int,
        listas: json['listas'] == null ? null : json['listas'] as int,
        perdidas: json['perdidas'] == null ? null : json['perdidas'] as int,
      );

  Map<String, dynamic> toJson() => {
        if (germinadas != null) 'germinadas': germinadas!,
        if (listas != null) 'listas': listas!,
        if (perdidas != null) 'perdidas': perdidas!,
      };
}

class PropagacionCrear {
  final String fincaId;
  final String cultivoId;
  final String metodo;
  final DateTime fechaInicio;
  final int puestas;

  const PropagacionCrear({
    required this.fincaId,
    required this.cultivoId,
    required this.metodo,
    required this.fechaInicio,
    required this.puestas,
  });

  factory PropagacionCrear.fromJson(Map<String, dynamic> json) => PropagacionCrear(
        fincaId: json['finca_id'] as String,
        cultivoId: json['cultivo_id'] as String,
        metodo: json['metodo'] as String,
        fechaInicio: DateTime.parse(json['fecha_inicio'] as String),
        puestas: json['puestas'] as int,
      );

  Map<String, dynamic> toJson() => {
        'finca_id': fincaId,
        'cultivo_id': cultivoId,
        'metodo': metodo,
        'fecha_inicio': fechaInicio.toIso8601String().substring(0, 10),
        'puestas': puestas,
      };
}

class PropagacionSalida {
  final String id;
  final String fincaId;
  final String cultivoId;
  final String? siembraId;
  final String metodo;
  final DateTime fechaInicio;
  final int puestas;
  final int germinadas;
  final int listas;
  final int perdidas;
  final int trasplantadas;

  const PropagacionSalida({
    required this.id,
    required this.fincaId,
    required this.cultivoId,
    this.siembraId,
    required this.metodo,
    required this.fechaInicio,
    required this.puestas,
    required this.germinadas,
    required this.listas,
    required this.perdidas,
    required this.trasplantadas,
  });

  factory PropagacionSalida.fromJson(Map<String, dynamic> json) => PropagacionSalida(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        cultivoId: json['cultivo_id'] as String,
        siembraId: json['siembra_id'] == null ? null : json['siembra_id'] as String,
        metodo: json['metodo'] as String,
        fechaInicio: DateTime.parse(json['fecha_inicio'] as String),
        puestas: json['puestas'] as int,
        germinadas: json['germinadas'] as int,
        listas: json['listas'] as int,
        perdidas: json['perdidas'] as int,
        trasplantadas: json['trasplantadas'] as int,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'cultivo_id': cultivoId,
        if (siembraId != null) 'siembra_id': siembraId!,
        'metodo': metodo,
        'fecha_inicio': fechaInicio.toIso8601String().substring(0, 10),
        'puestas': puestas,
        'germinadas': germinadas,
        'listas': listas,
        'perdidas': perdidas,
        'trasplantadas': trasplantadas,
      };
}

class ProyeccionAgricolaEntrada {
  final String cultivoId;
  final double areaM2;

  const ProyeccionAgricolaEntrada({
    required this.cultivoId,
    required this.areaM2,
  });

  factory ProyeccionAgricolaEntrada.fromJson(Map<String, dynamic> json) => ProyeccionAgricolaEntrada(
        cultivoId: json['cultivo_id'] as String,
        areaM2: (json['area_m2'] as num).toDouble(),
      );

  Map<String, dynamic> toJson() => {
        'cultivo_id': cultivoId,
        'area_m2': areaM2,
      };
}

class ProyeccionAgricolaSalida {
  final String areaM2;
  final String cultivoNombre;
  final int plantasEstimadas;
  final int? mesesPrimeraCosecha;
  final String? cosechasPorAnio;
  final String costoSemillaEstimado;
  final String costoAbonoEstimado;
  final String ingresoEstimadoAnual;
  final String utilidadEstimadaAnual;

  const ProyeccionAgricolaSalida({
    required this.areaM2,
    required this.cultivoNombre,
    required this.plantasEstimadas,
    this.mesesPrimeraCosecha,
    this.cosechasPorAnio,
    required this.costoSemillaEstimado,
    required this.costoAbonoEstimado,
    required this.ingresoEstimadoAnual,
    required this.utilidadEstimadaAnual,
  });

  factory ProyeccionAgricolaSalida.fromJson(Map<String, dynamic> json) => ProyeccionAgricolaSalida(
        areaM2: json['area_m2'] as String,
        cultivoNombre: json['cultivo_nombre'] as String,
        plantasEstimadas: json['plantas_estimadas'] as int,
        mesesPrimeraCosecha: json['meses_primera_cosecha'] == null ? null : json['meses_primera_cosecha'] as int,
        cosechasPorAnio: json['cosechas_por_anio'] == null ? null : json['cosechas_por_anio'] as String,
        costoSemillaEstimado: json['costo_semilla_estimado'] as String,
        costoAbonoEstimado: json['costo_abono_estimado'] as String,
        ingresoEstimadoAnual: json['ingreso_estimado_anual'] as String,
        utilidadEstimadaAnual: json['utilidad_estimada_anual'] as String,
      );

  Map<String, dynamic> toJson() => {
        'area_m2': areaM2,
        'cultivo_nombre': cultivoNombre,
        'plantas_estimadas': plantasEstimadas,
        if (mesesPrimeraCosecha != null) 'meses_primera_cosecha': mesesPrimeraCosecha!,
        if (cosechasPorAnio != null) 'cosechas_por_anio': cosechasPorAnio!,
        'costo_semilla_estimado': costoSemillaEstimado,
        'costo_abono_estimado': costoAbonoEstimado,
        'ingreso_estimado_anual': ingresoEstimadoAnual,
        'utilidad_estimada_anual': utilidadEstimadaAnual,
      };
}

class ReadyResponse {
  final String status;
  final String service;
  final String version;
  final String baseDeDatos;

  const ReadyResponse({
    required this.status,
    required this.service,
    required this.version,
    required this.baseDeDatos,
  });

  factory ReadyResponse.fromJson(Map<String, dynamic> json) => ReadyResponse(
        status: json['status'] as String,
        service: json['service'] as String,
        version: json['version'] as String,
        baseDeDatos: json['base_de_datos'] as String,
      );

  Map<String, dynamic> toJson() => {
        'status': status,
        'service': service,
        'version': version,
        'base_de_datos': baseDeDatos,
      };
}

class ReporteCronograma {
  final List<CicloCronograma> ciclos;

  const ReporteCronograma({
    required this.ciclos,
  });

  factory ReporteCronograma.fromJson(Map<String, dynamic> json) => ReporteCronograma(
        ciclos: (json['ciclos'] as List<dynamic>).map((x) => CicloCronograma.fromJson(x as Map<String, dynamic>)).toList(),
      );

  Map<String, dynamic> toJson() => {
        'ciclos': ciclos.map((x) => x.toJson()).toList(),
      };
}

class ReporteDisponible {
  final String id;
  final String titulo;
  final String descripcion;
  final bool disponible;
  final String? motivo;
  final List<String> roles;

  const ReporteDisponible({
    required this.id,
    required this.titulo,
    required this.descripcion,
    required this.disponible,
    this.motivo,
    required this.roles,
  });

  factory ReporteDisponible.fromJson(Map<String, dynamic> json) => ReporteDisponible(
        id: json['id'] as String,
        titulo: json['titulo'] as String,
        descripcion: json['descripcion'] as String,
        disponible: json['disponible'] as bool,
        motivo: json['motivo'] == null ? null : json['motivo'] as String,
        roles: (json['roles'] as List<dynamic>).map((x) => x as String).toList(),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'titulo': titulo,
        'descripcion': descripcion,
        'disponible': disponible,
        if (motivo != null) 'motivo': motivo!,
        'roles': roles.map((x) => x).toList(),
      };
}

class ReporteEventos {
  final DateTime? desde;
  final DateTime? hasta;
  final int total;
  final double perdidaEstimadaTotal;
  final List<EventosPorTipo> porTipo;
  final Map<String, dynamic> porSeveridad;
  final String? aviso;

  const ReporteEventos({
    this.desde,
    this.hasta,
    required this.total,
    required this.perdidaEstimadaTotal,
    required this.porTipo,
    required this.porSeveridad,
    this.aviso,
  });

  factory ReporteEventos.fromJson(Map<String, dynamic> json) => ReporteEventos(
        desde: json['desde'] == null ? null : DateTime.parse(json['desde'] as String),
        hasta: json['hasta'] == null ? null : DateTime.parse(json['hasta'] as String),
        total: json['total'] as int,
        perdidaEstimadaTotal: (json['perdida_estimada_total'] as num).toDouble(),
        porTipo: (json['por_tipo'] as List<dynamic>).map((x) => EventosPorTipo.fromJson(x as Map<String, dynamic>)).toList(),
        porSeveridad: json['por_severidad'] as Map<String, dynamic>,
        aviso: json['aviso'] == null ? null : json['aviso'] as String,
      );

  Map<String, dynamic> toJson() => {
        if (desde != null) 'desde': desde!.toIso8601String().substring(0, 10),
        if (hasta != null) 'hasta': hasta!.toIso8601String().substring(0, 10),
        'total': total,
        'perdida_estimada_total': perdidaEstimadaTotal,
        'por_tipo': porTipo.map((x) => x.toJson()).toList(),
        'por_severidad': porSeveridad,
        if (aviso != null) 'aviso': aviso!,
      };
}

class ReporteIndices {
  final List<IndiceSiembra> siembras;

  const ReporteIndices({
    required this.siembras,
  });

  factory ReporteIndices.fromJson(Map<String, dynamic> json) => ReporteIndices(
        siembras: (json['siembras'] as List<dynamic>).map((x) => IndiceSiembra.fromJson(x as Map<String, dynamic>)).toList(),
      );

  Map<String, dynamic> toJson() => {
        'siembras': siembras.map((x) => x.toJson()).toList(),
      };
}

class RespuestaAsistente {
  final String loQueEntendi;
  final List<CausaProbable> causasProbables;
  final List<String> queHacer;
  final List<TratamientoValidado> tratamientos;
  final String mensajeTratamiento;
  final String cuandoLlamarAlTecnico;
  final String aviso;
  final bool hayInformacion;

  const RespuestaAsistente({
    required this.loQueEntendi,
    required this.causasProbables,
    required this.queHacer,
    required this.tratamientos,
    required this.mensajeTratamiento,
    required this.cuandoLlamarAlTecnico,
    required this.aviso,
    required this.hayInformacion,
  });

  factory RespuestaAsistente.fromJson(Map<String, dynamic> json) => RespuestaAsistente(
        loQueEntendi: json['lo_que_entendi'] as String,
        causasProbables: (json['causas_probables'] as List<dynamic>).map((x) => CausaProbable.fromJson(x as Map<String, dynamic>)).toList(),
        queHacer: (json['que_hacer'] as List<dynamic>).map((x) => x as String).toList(),
        tratamientos: (json['tratamientos'] as List<dynamic>).map((x) => TratamientoValidado.fromJson(x as Map<String, dynamic>)).toList(),
        mensajeTratamiento: json['mensaje_tratamiento'] as String,
        cuandoLlamarAlTecnico: json['cuando_llamar_al_tecnico'] as String,
        aviso: json['aviso'] as String,
        hayInformacion: json['hay_informacion'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'lo_que_entendi': loQueEntendi,
        'causas_probables': causasProbables.map((x) => x.toJson()).toList(),
        'que_hacer': queHacer.map((x) => x).toList(),
        'tratamientos': tratamientos.map((x) => x.toJson()).toList(),
        'mensaje_tratamiento': mensajeTratamiento,
        'cuando_llamar_al_tecnico': cuandoLlamarAlTecnico,
        'aviso': aviso,
        'hay_informacion': hayInformacion,
      };
}

class RetroalimentacionEntrada {
  final String valor;
  final String? comentario;

  const RetroalimentacionEntrada({
    required this.valor,
    this.comentario,
  });

  factory RetroalimentacionEntrada.fromJson(Map<String, dynamic> json) => RetroalimentacionEntrada(
        valor: json['valor'] as String,
        comentario: json['comentario'] == null ? null : json['comentario'] as String,
      );

  Map<String, dynamic> toJson() => {
        'valor': valor,
        if (comentario != null) 'comentario': comentario!,
      };
}

class RetroalimentacionSalida {
  final String mensajeId;
  final String valor;
  final String? comentario;

  const RetroalimentacionSalida({
    required this.mensajeId,
    required this.valor,
    this.comentario,
  });

  factory RetroalimentacionSalida.fromJson(Map<String, dynamic> json) => RetroalimentacionSalida(
        mensajeId: json['mensaje_id'] as String,
        valor: json['valor'] as String,
        comentario: json['comentario'] == null ? null : json['comentario'] as String,
      );

  Map<String, dynamic> toJson() => {
        'mensaje_id': mensajeId,
        'valor': valor,
        if (comentario != null) 'comentario': comentario!,
      };
}

class RiesgoCrear {
  final String nombre;
  final String tipo;
  final String aplicaA;

  const RiesgoCrear({
    required this.nombre,
    required this.tipo,
    required this.aplicaA,
  });

  factory RiesgoCrear.fromJson(Map<String, dynamic> json) => RiesgoCrear(
        nombre: json['nombre'] as String,
        tipo: json['tipo'] as String,
        aplicaA: json['aplica_a'] as String,
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        'tipo': tipo,
        'aplica_a': aplicaA,
      };
}

class RiesgoSalida {
  final String id;
  final String nombre;
  final String tipo;
  final String aplicaA;

  const RiesgoSalida({
    required this.id,
    required this.nombre,
    required this.tipo,
    required this.aplicaA,
  });

  factory RiesgoSalida.fromJson(Map<String, dynamic> json) => RiesgoSalida(
        id: json['id'] as String,
        nombre: json['nombre'] as String,
        tipo: json['tipo'] as String,
        aplicaA: json['aplica_a'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'nombre': nombre,
        'tipo': tipo,
        'aplica_a': aplicaA,
      };
}

class SiembraCrear {
  final String fincaId;
  final String loteId;
  final String cultivoId;
  final String metodo;
  final double areaHa;
  final int? plantasSembradas;
  final DateTime fechaPlan;
  final double? presupuesto;

  const SiembraCrear({
    required this.fincaId,
    required this.loteId,
    required this.cultivoId,
    required this.metodo,
    required this.areaHa,
    this.plantasSembradas,
    required this.fechaPlan,
    this.presupuesto,
  });

  factory SiembraCrear.fromJson(Map<String, dynamic> json) => SiembraCrear(
        fincaId: json['finca_id'] as String,
        loteId: json['lote_id'] as String,
        cultivoId: json['cultivo_id'] as String,
        metodo: json['metodo'] as String,
        areaHa: (json['area_ha'] as num).toDouble(),
        plantasSembradas: json['plantas_sembradas'] == null ? null : json['plantas_sembradas'] as int,
        fechaPlan: DateTime.parse(json['fecha_plan'] as String),
        presupuesto: json['presupuesto'] == null ? null : (json['presupuesto'] as num).toDouble(),
      );

  Map<String, dynamic> toJson() => {
        'finca_id': fincaId,
        'lote_id': loteId,
        'cultivo_id': cultivoId,
        'metodo': metodo,
        'area_ha': areaHa,
        if (plantasSembradas != null) 'plantas_sembradas': plantasSembradas!,
        'fecha_plan': fechaPlan.toIso8601String().substring(0, 10),
        if (presupuesto != null) 'presupuesto': presupuesto!,
      };
}

class SiembraResumen {
  final String id;
  final String fincaId;
  final String loteId;
  final String cultivoId;
  final String metodo;
  final double areaHa;
  final int? plantasSembradas;
  final DateTime fechaPlan;
  final String estado;

  const SiembraResumen({
    required this.id,
    required this.fincaId,
    required this.loteId,
    required this.cultivoId,
    required this.metodo,
    required this.areaHa,
    this.plantasSembradas,
    required this.fechaPlan,
    required this.estado,
  });

  factory SiembraResumen.fromJson(Map<String, dynamic> json) => SiembraResumen(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        loteId: json['lote_id'] as String,
        cultivoId: json['cultivo_id'] as String,
        metodo: json['metodo'] as String,
        areaHa: (json['area_ha'] as num).toDouble(),
        plantasSembradas: json['plantas_sembradas'] == null ? null : json['plantas_sembradas'] as int,
        fechaPlan: DateTime.parse(json['fecha_plan'] as String),
        estado: json['estado'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'lote_id': loteId,
        'cultivo_id': cultivoId,
        'metodo': metodo,
        'area_ha': areaHa,
        if (plantasSembradas != null) 'plantas_sembradas': plantasSembradas!,
        'fecha_plan': fechaPlan.toIso8601String().substring(0, 10),
        'estado': estado,
      };
}

class SiembraSalida {
  final String id;
  final String fincaId;
  final String loteId;
  final String cultivoId;
  final String metodo;
  final double areaHa;
  final int? plantasSembradas;
  final DateTime fechaPlan;
  final String estado;
  final double? presupuesto;
  final List<CicloSalida> ciclos;

  const SiembraSalida({
    required this.id,
    required this.fincaId,
    required this.loteId,
    required this.cultivoId,
    required this.metodo,
    required this.areaHa,
    this.plantasSembradas,
    required this.fechaPlan,
    required this.estado,
    this.presupuesto,
    required this.ciclos,
  });

  factory SiembraSalida.fromJson(Map<String, dynamic> json) => SiembraSalida(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        loteId: json['lote_id'] as String,
        cultivoId: json['cultivo_id'] as String,
        metodo: json['metodo'] as String,
        areaHa: (json['area_ha'] as num).toDouble(),
        plantasSembradas: json['plantas_sembradas'] == null ? null : json['plantas_sembradas'] as int,
        fechaPlan: DateTime.parse(json['fecha_plan'] as String),
        estado: json['estado'] as String,
        presupuesto: json['presupuesto'] == null ? null : (json['presupuesto'] as num).toDouble(),
        ciclos: (json['ciclos'] as List<dynamic>).map((x) => CicloSalida.fromJson(x as Map<String, dynamic>)).toList(),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'lote_id': loteId,
        'cultivo_id': cultivoId,
        'metodo': metodo,
        'area_ha': areaHa,
        if (plantasSembradas != null) 'plantas_sembradas': plantasSembradas!,
        'fecha_plan': fechaPlan.toIso8601String().substring(0, 10),
        'estado': estado,
        if (presupuesto != null) 'presupuesto': presupuesto!,
        'ciclos': ciclos.map((x) => x.toJson()).toList(),
      };
}

class SintomaEntrada {
  final String descripcion;
  final String? parte;
  final String? faseOEdad;

  const SintomaEntrada({
    required this.descripcion,
    this.parte,
    this.faseOEdad,
  });

  factory SintomaEntrada.fromJson(Map<String, dynamic> json) => SintomaEntrada(
        descripcion: json['descripcion'] as String,
        parte: json['parte'] == null ? null : json['parte'] as String,
        faseOEdad: json['fase_o_edad'] == null ? null : json['fase_o_edad'] as String,
      );

  Map<String, dynamic> toJson() => {
        'descripcion': descripcion,
        if (parte != null) 'parte': parte!,
        if (faseOEdad != null) 'fase_o_edad': faseOEdad!,
      };
}

class SintomaSalida {
  final String descripcion;
  final String? parte;
  final String? faseOEdad;

  const SintomaSalida({
    required this.descripcion,
    this.parte,
    this.faseOEdad,
  });

  factory SintomaSalida.fromJson(Map<String, dynamic> json) => SintomaSalida(
        descripcion: json['descripcion'] as String,
        parte: json['parte'] == null ? null : json['parte'] as String,
        faseOEdad: json['fase_o_edad'] == null ? null : json['fase_o_edad'] as String,
      );

  Map<String, dynamic> toJson() => {
        'descripcion': descripcion,
        if (parte != null) 'parte': parte!,
        if (faseOEdad != null) 'fase_o_edad': faseOEdad!,
      };
}

class TerminoSalida {
  final String id;
  final String termino;
  final String explicacion;
  final String categoria;

  const TerminoSalida({
    required this.id,
    required this.termino,
    required this.explicacion,
    required this.categoria,
  });

  factory TerminoSalida.fromJson(Map<String, dynamic> json) => TerminoSalida(
        id: json['id'] as String,
        termino: json['termino'] as String,
        explicacion: json['explicacion'] as String,
        categoria: json['categoria'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'termino': termino,
        'explicacion': explicacion,
        'categoria': categoria,
      };
}

class TokenResponse {
  final String accessToken;
  final String? tokenType;
  final int expiresIn;
  final String rol;
  final String nombre;

  const TokenResponse({
    required this.accessToken,
    this.tokenType,
    required this.expiresIn,
    required this.rol,
    required this.nombre,
  });

  factory TokenResponse.fromJson(Map<String, dynamic> json) => TokenResponse(
        accessToken: json['access_token'] as String,
        tokenType: json['token_type'] == null ? null : json['token_type'] as String,
        expiresIn: json['expires_in'] as int,
        rol: json['rol'] as String,
        nombre: json['nombre'] as String,
      );

  Map<String, dynamic> toJson() => {
        'access_token': accessToken,
        if (tokenType != null) 'token_type': tokenType!,
        'expires_in': expiresIn,
        'rol': rol,
        'nombre': nombre,
      };
}

class TrabajadorCreate {
  final String nombre;
  final String tipo;
  final double jornalHabitual;
  final String? documento;
  final String? telefono;

  const TrabajadorCreate({
    required this.nombre,
    required this.tipo,
    required this.jornalHabitual,
    this.documento,
    this.telefono,
  });

  factory TrabajadorCreate.fromJson(Map<String, dynamic> json) => TrabajadorCreate(
        nombre: json['nombre'] as String,
        tipo: json['tipo'] as String,
        jornalHabitual: (json['jornal_habitual'] as num).toDouble(),
        documento: json['documento'] == null ? null : json['documento'] as String,
        telefono: json['telefono'] == null ? null : json['telefono'] as String,
      );

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        'tipo': tipo,
        'jornal_habitual': jornalHabitual,
        if (documento != null) 'documento': documento!,
        if (telefono != null) 'telefono': telefono!,
      };
}

class TrabajadorResponse {
  final String id;
  final String fincaId;
  final String nombre;
  final String tipo;
  final String jornalHabitual;
  final String? documentoUltimos4;
  final String? telefono;
  final String estado;

  const TrabajadorResponse({
    required this.id,
    required this.fincaId,
    required this.nombre,
    required this.tipo,
    required this.jornalHabitual,
    this.documentoUltimos4,
    this.telefono,
    required this.estado,
  });

  factory TrabajadorResponse.fromJson(Map<String, dynamic> json) => TrabajadorResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        nombre: json['nombre'] as String,
        tipo: json['tipo'] as String,
        jornalHabitual: json['jornal_habitual'] as String,
        documentoUltimos4: json['documento_ultimos4'] == null ? null : json['documento_ultimos4'] as String,
        telefono: json['telefono'] == null ? null : json['telefono'] as String,
        estado: json['estado'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        'nombre': nombre,
        'tipo': tipo,
        'jornal_habitual': jornalHabitual,
        if (documentoUltimos4 != null) 'documento_ultimos4': documentoUltimos4!,
        if (telefono != null) 'telefono': telefono!,
        'estado': estado,
      };
}

class TrabajadorUpdate {
  final String? nombre;
  final String? tipo;
  final double? jornalHabitual;
  final String? documento;
  final String? telefono;

  const TrabajadorUpdate({
    this.nombre,
    this.tipo,
    this.jornalHabitual,
    this.documento,
    this.telefono,
  });

  factory TrabajadorUpdate.fromJson(Map<String, dynamic> json) => TrabajadorUpdate(
        nombre: json['nombre'] == null ? null : json['nombre'] as String,
        tipo: json['tipo'] == null ? null : json['tipo'] as String,
        jornalHabitual: json['jornal_habitual'] == null ? null : (json['jornal_habitual'] as num).toDouble(),
        documento: json['documento'] == null ? null : json['documento'] as String,
        telefono: json['telefono'] == null ? null : json['telefono'] as String,
      );

  Map<String, dynamic> toJson() => {
        if (nombre != null) 'nombre': nombre!,
        if (tipo != null) 'tipo': tipo!,
        if (jornalHabitual != null) 'jornal_habitual': jornalHabitual!,
        if (documento != null) 'documento': documento!,
        if (telefono != null) 'telefono': telefono!,
      };
}

class TrasplanteEntrada {
  final String siembraId;
  final int cantidad;

  const TrasplanteEntrada({
    required this.siembraId,
    required this.cantidad,
  });

  factory TrasplanteEntrada.fromJson(Map<String, dynamic> json) => TrasplanteEntrada(
        siembraId: json['siembra_id'] as String,
        cantidad: json['cantidad'] as int,
      );

  Map<String, dynamic> toJson() => {
        'siembra_id': siembraId,
        'cantidad': cantidad,
      };
}

class TratamientoValidado {
  final String problema;
  final String productoIca;
  final String descripcion;
  final String? fuente;

  const TratamientoValidado({
    required this.problema,
    required this.productoIca,
    required this.descripcion,
    this.fuente,
  });

  factory TratamientoValidado.fromJson(Map<String, dynamic> json) => TratamientoValidado(
        problema: json['problema'] as String,
        productoIca: json['producto_ica'] as String,
        descripcion: json['descripcion'] as String,
        fuente: json['fuente'] == null ? null : json['fuente'] as String,
      );

  Map<String, dynamic> toJson() => {
        'problema': problema,
        'producto_ica': productoIca,
        'descripcion': descripcion,
        if (fuente != null) 'fuente': fuente!,
      };
}

class UsuarioCreate {
  final String email;
  final String nombre;
  final String password;
  final String? rol;

  const UsuarioCreate({
    required this.email,
    required this.nombre,
    required this.password,
    this.rol,
  });

  factory UsuarioCreate.fromJson(Map<String, dynamic> json) => UsuarioCreate(
        email: json['email'] as String,
        nombre: json['nombre'] as String,
        password: json['password'] as String,
        rol: json['rol'] == null ? null : json['rol'] as String,
      );

  Map<String, dynamic> toJson() => {
        'email': email,
        'nombre': nombre,
        'password': password,
        if (rol != null) 'rol': rol!,
      };
}

class UsuarioResponse {
  final String id;
  final String email;
  final String nombre;
  final String rol;
  final bool activo;

  const UsuarioResponse({
    required this.id,
    required this.email,
    required this.nombre,
    required this.rol,
    required this.activo,
  });

  factory UsuarioResponse.fromJson(Map<String, dynamic> json) => UsuarioResponse(
        id: json['id'] as String,
        email: json['email'] as String,
        nombre: json['nombre'] as String,
        rol: json['rol'] as String,
        activo: json['activo'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'nombre': nombre,
        'rol': rol,
        'activo': activo,
      };
}

class ValidacionSalida {
  final String estado;
  final String expertoId;
  final String? observacion;
  final DateTime creadoEn;

  const ValidacionSalida({
    required this.estado,
    required this.expertoId,
    this.observacion,
    required this.creadoEn,
  });

  factory ValidacionSalida.fromJson(Map<String, dynamic> json) => ValidacionSalida(
        estado: json['estado'] as String,
        expertoId: json['experto_id'] as String,
        observacion: json['observacion'] == null ? null : json['observacion'] as String,
        creadoEn: DateTime.parse(json['creado_en'] as String),
      );

  Map<String, dynamic> toJson() => {
        'estado': estado,
        'experto_id': expertoId,
        if (observacion != null) 'observacion': observacion!,
        'creado_en': creadoEn.toUtc().toIso8601String(),
      };
}

class VentaCreate {
  final String? comprador;
  final DateTime fecha;
  final List<LineaVentaCreate> lineas;

  const VentaCreate({
    this.comprador,
    required this.fecha,
    required this.lineas,
  });

  factory VentaCreate.fromJson(Map<String, dynamic> json) => VentaCreate(
        comprador: json['comprador'] == null ? null : json['comprador'] as String,
        fecha: DateTime.parse(json['fecha'] as String),
        lineas: (json['lineas'] as List<dynamic>).map((x) => LineaVentaCreate.fromJson(x as Map<String, dynamic>)).toList(),
      );

  Map<String, dynamic> toJson() => {
        if (comprador != null) 'comprador': comprador!,
        'fecha': fecha.toUtc().toIso8601String(),
        'lineas': lineas.map((x) => x.toJson()).toList(),
      };
}

class VentaResponse {
  final String id;
  final String fincaId;
  final String? comprador;
  final DateTime fecha;
  final String estado;
  final String total;

  const VentaResponse({
    required this.id,
    required this.fincaId,
    this.comprador,
    required this.fecha,
    required this.estado,
    required this.total,
  });

  factory VentaResponse.fromJson(Map<String, dynamic> json) => VentaResponse(
        id: json['id'] as String,
        fincaId: json['finca_id'] as String,
        comprador: json['comprador'] == null ? null : json['comprador'] as String,
        fecha: DateTime.parse(json['fecha'] as String),
        estado: json['estado'] as String,
        total: json['total'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'finca_id': fincaId,
        if (comprador != null) 'comprador': comprador!,
        'fecha': fecha.toUtc().toIso8601String(),
        'estado': estado,
        'total': total,
      };
}
