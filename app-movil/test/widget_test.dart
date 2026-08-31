// Pruebas de widget de la aplicacion del paciente.
//
// Cubren el arranque y la validacion del formulario de acceso (RF01). No
// tocan la red: comprobar el registro de tomas contra el API es trabajo de
// las pruebas del backend, que ya verifican la idempotencia del envio.

import 'package:cdss_adherencia/main.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  setUp(() {
    // Sin valores iniciales no hay sesion guardada: la aplicacion debe
    // terminar mostrando la pantalla de acceso.
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('sin sesion guardada se muestra la pantalla de acceso',
      (tester) async {
    await tester.pumpWidget(const AplicacionPaciente());
    await tester.pumpAndSettle();

    expect(find.text('Mi tratamiento'), findsOneWidget);
    expect(find.text('Ingresar'), findsOneWidget);
    expect(find.text('Correo electrónico'), findsOneWidget);
  });

  testWidgets('el formulario de acceso rechaza los campos vacios',
      (tester) async {
    await tester.pumpWidget(const AplicacionPaciente());
    await tester.pumpAndSettle();

    await tester.tap(find.text('Ingresar'));
    await tester.pump();

    expect(find.text('Escriba su correo.'), findsOneWidget);
    expect(find.text('Escriba su contraseña.'), findsOneWidget);
  });

  testWidgets('un correo sin arroba no supera la validacion', (tester) async {
    await tester.pumpWidget(const AplicacionPaciente());
    await tester.pumpAndSettle();

    await tester.enterText(find.byType(TextFormField).first, 'correo-invalido');
    await tester.tap(find.text('Ingresar'));
    await tester.pump();

    expect(find.text('El correo no parece válido.'), findsOneWidget);
  });
}
