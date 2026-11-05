# Publicação do RarePedigree Studio Web

## Arquitetura de publicação

O site é uma aplicação React/Vite estática em `web/`. A introdução 3D é carregada de forma
assíncrona e o editor científico funciona no navegador sem transmitir projetos a um servidor.

## Ambientes

- Desenvolvimento: `http://127.0.0.1:5173/` (ou a porta informada pelo Vite).
- Produção: `https://jv130397.github.io/RarePedigree-Studio/`.
- Caminho-base de produção: `/RarePedigree-Studio/`.

## Pipeline

O workflow `.github/workflows/deploy-pages.yml` executa:

1. instalação reproduzível com `pnpm-lock.yaml`;
2. testes Vitest;
3. verificação TypeScript e build Vite;
4. criação de `404.html` para recuperação da SPA;
5. publicação do artefato no GitHub Pages.

Pull requests executam validação, mas não publicam. Pushes na `main` e execuções manuais podem
publicar.

## Ativação inicial

No repositório GitHub, selecione **Settings → Pages → Build and deployment → Source → GitHub
Actions**. Depois, envie o workflow para a branch `main`.

## Limitações

- Não existe backend ou autenticação nesta etapa.
- Projetos são processados localmente no navegador.
- O site não está autorizado para uso diagnóstico ou armazenamento de dados clínicos reais.
