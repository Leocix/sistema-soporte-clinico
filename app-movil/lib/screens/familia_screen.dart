import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../models/familia.dart';
import '../services/api_service.dart';
import '../utils/tema.dart';
import '../widgets/mensaje_estado.dart';

/// Grupo familiar de acompanamiento, visto por el paciente (RF09).
///
/// La pantalla existe para resolver el punto debil del registro de adherencia:
/// hasta ahora la unica fuente de cada toma era el propio paciente. Un
/// conviviente que confirme la dosis anade un segundo testigo.
///
/// Todo el flujo parte del paciente: el invita, el retira. Es lo que separa un
/// acompanamiento consentido de una vigilancia, y por eso ni el medico ni el
/// familiar pueden iniciar el vinculo.
class FamiliaScreen extends StatefulWidget {
  const FamiliaScreen({super.key, required this.api});

  final ServicioApi api;

  @override
  State<FamiliaScreen> createState() => _FamiliaScreenState();
}

class _FamiliaScreenState extends State<FamiliaScreen> {
  List<Acompanante> _grupo = const [];
  bool _cargando = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    setState(() => _cargando = true);
    try {
      final grupo = await widget.api.miGrupoFamiliar();
      if (!mounted) return;
      setState(() {
        _grupo = grupo;
        _error = null;
        _cargando = false;
      });
    } on ErrorDeConexion {
      if (!mounted) return;
      setState(() {
        // A diferencia de las tomas, el grupo familiar no se puede gestionar
        // sin conexion: invitar exige que el servidor emita el codigo.
        _error = 'Sin conexión. Vuelva a intentarlo cuando tenga internet.';
        _cargando = false;
      });
    } on ErrorApi catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.mensaje;
        _cargando = false;
      });
    }
  }

  void _avisar(String texto, {bool exito = true}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(texto, style: const TextStyle(fontSize: 17)),
        backgroundColor: exito ? Tema.exito : Tema.peligro,
      ),
    );
  }

  Future<void> _invitar() async {
    final datos = await showModalBottomSheet<({String nombre, Parentesco parentesco})>(
      context: context,
      isScrollControlled: true,
      builder: (_) => const _FormularioInvitacion(),
    );
    if (datos == null) return;

    try {
      final nuevo = await widget.api.invitarFamiliar(
        nombre: datos.nombre,
        parentesco: datos.parentesco,
      );
      await _cargar();
      if (!mounted) return;
      await _mostrarCodigo(nuevo);
    } on ErrorDeConexion catch (e) {
      _avisar(e.mensaje, exito: false);
    } on ErrorApi catch (e) {
      _avisar(e.mensaje, exito: false);
    }
  }

  /// Muestra el codigo recien emitido con las instrucciones para usarlo.
  Future<void> _mostrarCodigo(Acompanante acompanante) async {
    final codigo = acompanante.codigoInvitacion;
    if (codigo == null) return;

    await showDialog<void>(
      context: context,
      builder: (contexto) => AlertDialog(
        title: const Text('Código de invitación'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Dele este código a ${acompanante.nombre}. Con él podrá crear '
              'su cuenta en esta misma aplicación y confirmar sus tomas.',
              style: const TextStyle(fontSize: 17, height: 1.4),
            ),
            const SizedBox(height: 16),
            _Codigo(codigo: codigo),
            const SizedBox(height: 12),
            Text(
              'El código vence en ${acompanante.diasParaVencer ?? 7} días.',
              style: const TextStyle(fontSize: 15, color: Tema.neutro),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Clipboard.setData(ClipboardData(text: codigo));
              _avisar('Código copiado.');
              Navigator.of(contexto).pop();
            },
            child: const Text('Copiar', style: TextStyle(fontSize: 17)),
          ),
          FilledButton(
            onPressed: () => Navigator.of(contexto).pop(),
            child: const Text('Listo'),
          ),
        ],
      ),
    );
  }

  Future<void> _retirar(Acompanante acompanante) async {
    final confirmado = await showDialog<bool>(
      context: context,
      builder: (contexto) => AlertDialog(
        title: Text(
          acompanante.pendiente ? '¿Anular la invitación?' : '¿Retirar a esta persona?',
        ),
        content: Text(
          acompanante.pendiente
              ? 'El código que le dio dejará de funcionar.'
              : '${acompanante.nombre} dejará de ver sus tomas y ya no podrá '
                  'confirmarlas. Las que ya confirmó se conservan.',
          style: const TextStyle(fontSize: 17),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(contexto).pop(false),
            child: const Text('Cancelar', style: TextStyle(fontSize: 17)),
          ),
          FilledButton(
            onPressed: () => Navigator.of(contexto).pop(true),
            style: FilledButton.styleFrom(backgroundColor: Tema.peligro),
            child: Text(acompanante.pendiente ? 'Anular' : 'Retirar'),
          ),
        ],
      ),
    );
    if (confirmado != true) return;

    try {
      await widget.api.retirarFamiliar(acompanante.id);
      await _cargar();
      _avisar('Listo.');
    } on ErrorDeConexion catch (e) {
      _avisar(e.mensaje, exito: false);
    } on ErrorApi catch (e) {
      _avisar(e.mensaje, exito: false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mi familia')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _invitar,
        icon: const Icon(Icons.person_add_alt),
        label: const Text('Invitar'),
      ),
      body: RefreshIndicator(
        onRefresh: _cargar,
        child: _cargando
            ? const Center(child: CircularProgressIndicator())
            : ListView(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
                children: [
                  const MensajeEstado(
                    texto: 'Invite a un familiar de confianza para que confirme '
                        'que usted tomó su medicina. Su médico verá un registro '
                        'respaldado por dos personas, no solo por usted.',
                  ),
                  if (_error != null)
                    MensajeEstado(
                      texto: _error!,
                      tono: TonoMensaje.aviso,
                      textoAccion: 'Reintentar',
                      accion: _cargar,
                    ),
                  if (_grupo.isEmpty && _error == null)
                    const _SinFamiliares()
                  else
                    ..._grupo.map(
                      (a) => _TarjetaAcompanante(
                        acompanante: a,
                        alRetirar: () => _retirar(a),
                        alVerCodigo: () => _mostrarCodigo(a),
                      ),
                    ),
                ],
              ),
      ),
    );
  }
}

/// Codigo de invitacion, en grande y espaciado para poder dictarlo.
class _Codigo extends StatelessWidget {
  const _Codigo({required this.codigo});

  final String codigo;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 16),
      decoration: BoxDecoration(
        color: Tema.fondo,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Tema.bordeTarjeta),
      ),
      child: Text(
        codigo,
        textAlign: TextAlign.center,
        style: const TextStyle(
          fontSize: 30,
          fontWeight: FontWeight.w800,
          // El espaciado ayuda a leerlo letra a letra al dictarlo por telefono.
          letterSpacing: 5,
          color: Tema.primarioOscuro,
        ),
      ),
    );
  }
}

class _TarjetaAcompanante extends StatelessWidget {
  const _TarjetaAcompanante({
    required this.acompanante,
    required this.alRetirar,
    required this.alVerCodigo,
  });

  final Acompanante acompanante;
  final VoidCallback alRetirar;
  final VoidCallback alVerCodigo;

  @override
  Widget build(BuildContext context) {
    final pendiente = acompanante.pendiente;

    return Card(
      color: Colors.white,
      elevation: 0,
      margin: Tema.margenTarjeta,
      shape: Tema.formaTarjeta,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 24,
                  backgroundColor: pendiente ? Tema.avisoFondo : Tema.exitoFondo,
                  child: Icon(
                    pendiente ? Icons.hourglass_top : Icons.verified_user_outlined,
                    color: pendiente ? Tema.aviso : Tema.exito,
                    size: 26,
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        acompanante.nombre,
                        style: const TextStyle(
                          fontSize: 19,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Text(
                        acompanante.parentesco.etiqueta,
                        style: const TextStyle(fontSize: 16, color: Tema.neutro),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  tooltip: pendiente ? 'Anular invitación' : 'Retirar',
                  icon: const Icon(Icons.delete_outline,
                      size: 26, color: Tema.peligro),
                  onPressed: alRetirar,
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (pendiente)
              Row(
                children: [
                  const Expanded(
                    child: Text(
                      'Todavía no ha creado su cuenta.',
                      style: TextStyle(fontSize: 16, color: Tema.aviso),
                    ),
                  ),
                  TextButton.icon(
                    onPressed: alVerCodigo,
                    icon: const Icon(Icons.key_outlined, size: 22),
                    label: const Text('Ver código',
                        style: TextStyle(fontSize: 16)),
                  ),
                ],
              )
            else
              Text(
                acompanante.tomasCorroboradas == 0
                    ? 'Aún no ha confirmado ninguna toma.'
                    : 'Ha confirmado ${acompanante.tomasCorroboradas} '
                        'toma(s) suyas.',
                style: const TextStyle(fontSize: 16, color: Tema.neutro),
              ),
          ],
        ),
      ),
    );
  }
}

class _SinFamiliares extends StatelessWidget {
  const _SinFamiliares();

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.white,
      elevation: 0,
      margin: Tema.margenTarjeta,
      shape: Tema.formaTarjeta,
      child: const Padding(
        padding: EdgeInsets.all(22),
        child: Column(
          children: [
            Icon(Icons.diversity_3_outlined, size: 56, color: Tema.neutro),
            SizedBox(height: 14),
            Text(
              'Todavía no ha invitado a nadie',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 19, fontWeight: FontWeight.w600),
            ),
            SizedBox(height: 8),
            Text(
              'Puede invitar hasta cinco personas. Usted decide quiénes son y '
              'puede retirarlas cuando quiera.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Tema.neutro),
            ),
          ],
        ),
      ),
    );
  }
}

/// Alta de una invitacion: a quien y con que vinculo.
class _FormularioInvitacion extends StatefulWidget {
  const _FormularioInvitacion();

  @override
  State<_FormularioInvitacion> createState() => _FormularioInvitacionState();
}

class _FormularioInvitacionState extends State<_FormularioInvitacion> {
  final _formulario = GlobalKey<FormState>();
  final _nombre = TextEditingController();
  Parentesco _parentesco = Parentesco.hijo;

  @override
  void dispose() {
    _nombre.dispose();
    super.dispose();
  }

  void _guardar() {
    if (!_formulario.currentState!.validate()) return;
    Navigator.of(context).pop(
      (nombre: _nombre.text.trim(), parentesco: _parentesco),
    );
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
            const Text(
              'Invitar a un familiar',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _nombre,
              style: const TextStyle(fontSize: 19),
              textCapitalization: TextCapitalization.words,
              decoration: const InputDecoration(
                labelText: '¿Cómo se llama?',
                hintText: 'Rosa',
              ),
              validator: (v) =>
                  (v ?? '').trim().length < 2 ? 'Escriba su nombre.' : null,
            ),
            const SizedBox(height: 14),
            DropdownButtonFormField<Parentesco>(
              initialValue: _parentesco,
              style: const TextStyle(fontSize: 19, color: Colors.black87),
              decoration: const InputDecoration(labelText: '¿Qué es suyo?'),
              items: Parentesco.values
                  .map(
                    (p) => DropdownMenuItem(
                      value: p,
                      child: Text(p.etiqueta,
                          style: const TextStyle(fontSize: 18)),
                    ),
                  )
                  .toList(),
              onChanged: (valor) =>
                  setState(() => _parentesco = valor ?? Parentesco.otro),
            ),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: _guardar,
              child: const Text('Generar código'),
            ),
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
