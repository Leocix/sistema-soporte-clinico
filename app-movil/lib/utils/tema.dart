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

    // No se escala el tema tipografico global con `fontSizeFactor`: varios
    // estilos del tema base llegan con `fontSize` nulo y `TextTheme.apply`
    // lanza una asercion en ese caso, lo que tumbaba la aplicacion al
    // arrancar. El tamano se fija de forma explicita en cada texto, que
    // ademas deja el criterio visible en el codigo en lugar de escondido en
    // un multiplicador.
    return base.copyWith(
      appBarTheme: const AppBarTheme(
        backgroundColor: primario,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          fontSize: 22,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
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
      // Barra inferior de navegacion: sustituye al menu de tres puntos, que
      // escondia funciones enteras detras de un icono sin etiqueta. Las
      // etiquetas se muestran siempre y los iconos van a 28 puntos, por la
      // misma razon que el resto de la interfaz (RNF03).
      navigationBarTheme: NavigationBarThemeData(
        height: 76,
        backgroundColor: Colors.white,
        indicatorColor: const Color(0xFFE8F1F8),
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        iconTheme: WidgetStateProperty.resolveWith(
          (estados) => IconThemeData(
            size: 28,
            color: estados.contains(WidgetState.selected)
                ? primarioOscuro
                : neutro,
          ),
        ),
        labelTextStyle: WidgetStateProperty.resolveWith(
          (estados) => TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: estados.contains(WidgetState.selected)
                ? primarioOscuro
                : neutro,
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
