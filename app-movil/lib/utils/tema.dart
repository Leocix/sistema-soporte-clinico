import 'package:flutter/material.dart';

/// Guia de estilo de la aplicacion del paciente.
///
/// El usuario objetivo es un adulto mayor polimedicado, de modo que las
/// decisiones visuales priorizan el tamano y el contraste sobre la densidad:
/// texto base de 18 puntos, areas tactiles de 56 puntos de alto y colores con
/// contraste suficiente para leerse a plena luz. Es la traduccion concreta de
/// RNF03 (usabilidad, meta SUS >= 80).
class Tema {
  Tema._();

  static const Color primario = Color(0xFF17608F);
  static const Color primarioOscuro = Color(0xFF114B6F);
  static const Color fondo = Color(0xFFF4F6FA);

  static const Color exito = Color(0xFF12704A);
  static const Color exitoFondo = Color(0xFFE7F5EE);
  static const Color aviso = Color(0xFF91610A);
  static const Color avisoFondo = Color(0xFFFDF4E3);
  static const Color peligro = Color(0xFFB3261E);
  static const Color peligroFondo = Color(0xFFFDECEB);
  static const Color neutro = Color(0xFF5C6B82);

  /// Altura minima de cualquier control que el paciente deba pulsar.
  static const double alturaBoton = 56;

  static const Color bordeTarjeta = Color(0xFFDDE3ED);

  /// Estilo comun de las tarjetas.
  ///
  /// Se aplica en cada `Card` en lugar de a traves de `ThemeData.cardTheme`
  /// porque esa propiedad cambio de tipo entre versiones de Flutter
  /// (`CardTheme` -> `CardThemeData`), y fijar cualquiera de las dos ataria el
  /// proyecto a un rango concreto de versiones del SDK.
  static const EdgeInsets margenTarjeta = EdgeInsets.only(bottom: 12);

  static RoundedRectangleBorder get formaTarjeta => RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: bordeTarjeta),
      );

  static ThemeData construir() {
    final base = ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primario,
        primary: primario,
      ),
      scaffoldBackgroundColor: fondo,
    );

    return base.copyWith(
      textTheme: base.textTheme.apply(fontSizeFactor: 1.15),
      appBarTheme: const AppBarTheme(
        backgroundColor: primario,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(alturaBoton),
          textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size.fromHeight(alturaBoton),
          textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 18,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
        ),
      ),
    );
  }
}
