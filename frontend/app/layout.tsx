import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Buscaí - Encontre serviços locais em Santarém',
  description: 'Plataforma de busca local para Santarém, Pará, Brasil',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  )
}
