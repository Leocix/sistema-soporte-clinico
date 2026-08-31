import 'package:flutter/material.dart';

import '../models/medicamento.dart';
import '../services/almacenamiento.dart';
import '../utils/tema.dart';
import '../widgets/mensaje_estado.dart';

/// Plan de tomas del paciente.
///
/// El plan se guarda **en el telefono**, no en el servidor: el modelo de datos
/// actual registra la carga terapeutica de forma agregada (numero de farmacos
/// y tomas al dia), no la lista nominal de prescripciones. Cuando el medico
/// gestione el esquema farmacologico desde el panel (Sprint 3), esta pantalla
/// pasara a mostrar lo prescrito en lugar de pedirselo al paciente, y lo que
/// hoy se escribe aqui servira para migrar los datos.
class PlanScreen extends StatefulWidget {
  const PlanScreen({super.key});

  @override
  State<PlanScreen> createState() => _PlanScreenState();
}

class _PlanScreenState extends State<PlanScreen> {
  List<Medicamento> _plan = const [];
  bool _cargando = true;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    final plan = await Almacenamiento.instancia.leerPlan();
    if (!mounted) return;
    setState(() {
      _plan = plan;
      _cargando = false;
    });
  }

  Future<void> _guardar(List<Medicamento> plan) async {
    await Almacenamiento.instancia.guardarPlan(plan);
    if (!mounted) return;
    setState(() => _plan = plan);
  }

  Future<void> _editar({Medicamento? existente}) async {
    final resultado = await showModalBottomSheet<Medicamento>(
      context: context,
      isScrollControlled: true,
      builder: (_) => _FormularioMedicamento(existente: existente),
    );
    if (resultado == null) return;

    final plan = List<Medicamento>.from(_plan);
    final indice = plan.indexWhere((m) => m.id == resultado.id);
    if (indice >= 0) {
      plan[indice] = resultado;
    } else {
      plan.add(resultado);
    }
    await _guardar(plan);
  }

  Future<void> _eliminar(Medicamento medicamento) async {
    final confirmado = await showDialog<bool>(
      context: context,
      builder: (contexto) => AlertDialog(
        title: const Text('¿Quitar del plan?'),
        content: Text(
          'Dejará de aparecer en la lista de hoy. Las tomas que ya registró '
          'de ${medicamento.nombre} se conservan.',
          style: const TextStyle(fontSize: 17),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(contexto).pop(false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(contexto).pop(true),
            style: FilledButton.styleFrom(backgroundColor: Tema.peligro),
            child: const Text('Quitar'),
          ),
        ],
      ),
    );

    if (confirmado != true) return;
    await _guardar(_plan.where((m) => m.id != medicamento.id).toList());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mis medicamentos')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _editar(),
        icon: const Icon(Icons.add),
        label: const Text('Agregar'),
      ),
      body: _cargando
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
              children: [
                const MensajeEstado(
                  texto: 'Registre aquí los medicamentos que le indicó su '
                      'médico y a qué hora los toma. Con eso la aplicación '
                      'arma su lista diaria.',
                ),
                if (_plan.isEmpty)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 40),
                    child: Text(
                      'Todavía no ha agregado ningún medicamento.',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 17, color: Tema.neutro),
                    ),
                  )
                else
                  ..._plan.map(
                    (medicamento) => Card(
                      color: Colors.white,
                      elevation: 0,
                      margin: Tema.margenTarjeta,
                      shape: Tema.formaTarjeta,
                      child: ListTile(
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 10,
                        ),
                        title: Text(
                          medicamento.nombre,
                          style: const TextStyle(
                            fontSize: 19,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        subtitle: Padding(
                          padding: const EdgeInsets.only(top: 4),
                          child: Text(
                            [
                              if (medicamento.dosis.isNotEmpty)
                                medicamento.dosis,
                              medicamento.horarios.join(' · '),
                            ].join('\n'),
                            style: const TextStyle(
                              fontSize: 16,
                              color: Tema.neutro,
                            ),
                          ),
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              tooltip: 'Editar',
                              icon: const Icon(Icons.edit_outlined, size: 26),
                              onPressed: () => _editar(existente: medicamento),
                            ),
                            IconButton(
                              tooltip: 'Quitar',
                              icon: const Icon(
                                Icons.delete_outline,
                                size: 26,
                                color: Tema.peligro,
                              ),
                              onPressed: () => _eliminar(medicamento),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
              ],
            ),
    );
  }
}

/// Alta y edicion de un medicamento del plan.
class _FormularioMedicamento extends StatefulWidget {
  const _FormularioMedicamento({this.existente});

  final Medicamento? existente;

  @override
  State<_FormularioMedicamento> createState() => _FormularioMedicamentoState();
}

class _FormularioMedicamentoState extends State<_FormularioMedicamento> {
  final _formulario = GlobalKey<FormState>();
  late final TextEditingController _nombre;
  late final TextEditingController _dosis;
  late List<String> _horarios;

  @override
  void initState() {
    super.initState();
    _nombre = TextEditingController(text: widget.existente?.nombre ?? '');
    _dosis = TextEditingController(text: widget.existente?.dosis ?? '');
    _horarios =
        List<String>.from(widget.existente?.horarios ?? const ['08:00']);
  }

  @override
  void dispose() {
    _nombre.dispose();
    _dosis.dispose();
    super.dispose();
  }

  Future<void> _agregarHorario() async {
    final hora = await showTimePicker(
      context: context,
      initialTime: const TimeOfDay(hour: 8, minute: 0),
      helpText: 'Hora de la toma',
    );
    if (hora == null) return;

    final texto = '${hora.hour.toString().padLeft(2, '0')}:'
        '${hora.minute.toString().padLeft(2, '0')}';
    if (_horarios.contains(texto)) return;

    setState(() {
      _horarios = [..._horarios, texto]..sort();
    });
  }

  void _guardar() {
    if (!_formulario.currentState!.validate()) return;
    if (_horarios.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Agregue al menos una hora de toma.')),
      );
      return;
    }

    final medicamento = Medicamento(
      // El identificador se conserva al editar: el plan es local, pero la
      // etiqueta del medicamento forma parte de la clave con la que el
      // servidor reconoce cada evento.
      id: widget.existente?.id ??
          DateTime.now().microsecondsSinceEpoch.toString(),
      nombre: _nombre.text.trim(),
      dosis: _dosis.text.trim(),
      horarios: _horarios,
    );
    Navigator.of(context).pop(medicamento);
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      child: Form(
        key: _formulario,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              widget.existente == null ? 'Nuevo medicamento' : 'Editar',
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _nombre,
              style: const TextStyle(fontSize: 19),
              textCapitalization: TextCapitalization.sentences,
              decoration: const InputDecoration(
                labelText: 'Nombre del medicamento',
                hintText: 'Losartán',
              ),
              validator: (v) =>
                  (v ?? '').trim().isEmpty ? 'Escriba el nombre.' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _dosis,
              style: const TextStyle(fontSize: 19),
              decoration: const InputDecoration(
                labelText: 'Dosis (opcional)',
                hintText: '50 mg',
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Horas de toma',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                ..._horarios.map(
                  (h) => InputChip(
                    label: Text(h, style: const TextStyle(fontSize: 17)),
                    onDeleted: () => setState(
                      () => _horarios = _horarios.where((x) => x != h).toList(),
                    ),
                  ),
                ),
                ActionChip(
                  avatar: const Icon(Icons.add, size: 20),
                  label: const Text('Agregar hora',
                      style: TextStyle(fontSize: 17)),
                  onPressed: _agregarHorario,
                ),
              ],
            ),
            const SizedBox(height: 24),
            FilledButton(onPressed: _guardar, child: const Text('Guardar')),
            const SizedBox(height: 8),
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancelar', style: TextStyle(fontSize: 17)),
            ),
          ],
        ),
      ),
    );
  }
}
