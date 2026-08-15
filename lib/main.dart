import 'package:flutter/material.dart';
import 'package:dynamic_color/dynamic_color.dart';

void main() => runApp(const MonApp());

// 2. Définis ta couleur de secours (Fallback) si Material You n'est pas dispo
const Color couleurSecours = Colors.deepPurple;

class MonApp extends StatelessWidget {
  const MonApp({super.key});

  @override
  Widget build(BuildContext context) {
    // 3. On entoure le MaterialApp avec DynamicColorBuilder
    return DynamicColorBuilder(
      builder: (ColorScheme? lightDynamic, ColorScheme? darkDynamic) {
        
        // --- THÈME CLAIR ---
        ColorScheme lightColorScheme;
        if (lightDynamic != null) {
          // Si le téléphone supporte Material You -> On utilise ses couleurs !
          lightColorScheme = lightDynamic.harmonized();
        } else {
          // SINON (Fallback) -> On génère une palette avec notre couleur de secours
          lightColorScheme = ColorScheme.fromSeed(
            seedColor: couleurSecours,
            brightness: Brightness.light,
          );
        }

        // --- THÈME SOMBRE ---
        ColorScheme darkColorScheme;
        if (darkDynamic != null) {
          darkColorScheme = darkDynamic.harmonized();
        } else {
          darkColorScheme = ColorScheme.fromSeed(
            seedColor: couleurSecours,
            brightness: Brightness.dark,
          );
        }

        // 4. On applique les couleurs à MaterialApp
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          themeMode: ThemeMode.system, // S'adapte au mode sombre/clair du téléphone
          
          theme: ThemeData(
            useMaterial3: true,
            colorScheme: lightColorScheme,
          ),
          darkTheme: ThemeData(
            useMaterial3: true,
            colorScheme: darkColorScheme,
          ),
          
          home: const PageAccueil(),
        );
      },
    );
  }
}

// Une petite page de test pour voir le résultat
class PageAccueil extends StatelessWidget {
  const PageAccueil({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Test Material You'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('Mes composants s\'adaptent au fond d\'écran !'),
            const SizedBox(height: 20),
            FilledButton(
              onPressed: () {},
              child: const Text('Bouton teinté'),
            ),
          ],
        ),
      ),
    );
  }
}