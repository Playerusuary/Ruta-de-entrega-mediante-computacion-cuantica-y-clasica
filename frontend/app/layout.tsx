import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Rutas de entrega - Clasico vs Cuantico",
  description:
    "Simulacion de rutas de entrega mediante computacion clasica y cuantica (mini TSP)",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
