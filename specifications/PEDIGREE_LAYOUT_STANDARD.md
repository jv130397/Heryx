# Padrão de layout de heredogramas

Este documento define invariantes obrigatórias para qualquer operação familiar nova. O renderer,
os comandos contextuais e futuros recursos clínicos não devem criar regras de posicionamento
paralelas.

## Invariantes verticais

- Pais ficam exatamente uma geração acima dos filhos.
- Parceiros registrados ficam na mesma geração.
- Irmãos com os mesmos pais ficam na mesma geração.
- Filhos biológicos, legais/adotivos, gestacionais ou sociais ficam uma geração abaixo.
- A legenda e outros elementos de interface nunca participam do enquadramento do heredograma.

## Invariantes horizontais

- Pessoas de uma parceria formam uma unidade familiar contígua.
- A distância interna padrão da unidade é `HORIZONTAL_SPACING` (130 unidades).
- Unidades familiares diferentes recebem `FAMILY_GAP` (220 unidades) entre suas extremidades.
- Duas pessoas desbloqueadas nunca podem receber a mesma coordenada.
- A ordem de unidades nas gerações inferiores usa a posição dos pais como âncora.

## Regras para novos filhos

- Sem parceiro registrado: é permitido registrar parentalidade monoparental.
- Exatamente um parceiro: ele é usado automaticamente como segundo genitor.
- Mais de um parceiro: o usuário deve selecionar explicitamente o outro genitor.
- Dois selecionados: o segundo deve possuir uma parceria registrada com o primeiro.
- A regra vale igualmente para filhos biológicos e legais/adotivos.

## Cobertura obrigatória

Qualquer alteração futura no layout deve testar: pai, mãe, casal de pais, pais desconhecidos,
parceiro, irmão, filho biológico, filho adotivo, duas famílias de avós e ausência de colisões.
