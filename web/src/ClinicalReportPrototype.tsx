import { Activity, AlertTriangle, ArrowLeft, BookOpen, CheckCircle2, Clock3, Dna, Download, FileText, Printer, ShieldCheck, Stethoscope, UserRound } from "lucide-react";
import "./ClinicalReportPrototype.css";

function MiniPedigree({ detailed = false }: { detailed?: boolean }) {
  return <svg className={`report-pedigree${detailed ? " detailed" : ""}`} viewBox="0 0 680 300" role="img" aria-label="Heredograma da família HRYX-024">
    <g className="rp-lines" fill="none">
      <path d="M160 60H280M220 60V130M440 60H560M500 60V130M220 130H500M360 130V205"/>
      <path d="M292 205H428M360 205V260"/>
    </g>
    <g className="rp-symbols">
      <rect x="132" y="32" width="56" height="56"/><circle cx="308" cy="60" r="28"/>
      <rect x="412" y="32" width="56" height="56"/><circle cx="588" cy="60" r="28"/>
      <rect x="192" y="102" width="56" height="56"/><circle cx="500" cy="130" r="28"/>
      <circle cx="264" cy="205" r="28"/><rect className="proband" x="332" y="177" width="56" height="56"/><circle cx="456" cy="205" r="28"/>
      <path className="proband-arrow" d="M312 247l28-20m-28 20l8-2m-8 2l3-8"/>
      {detailed && <><rect x="332" y="247" width="26" height="26"/><circle cx="395" cy="260" r="13"/></>}
    </g>
    <g className="rp-labels"><text x="160" y="106">I-1</text><text x="308" y="106">I-2</text><text x="440" y="106">I-3</text><text x="588" y="106">I-4</text><text x="220" y="176">II-1</text><text x="500" y="176">II-2</text><text x="264" y="251">III-1</text><text x="360" y="251">III-2</text><text x="456" y="251">III-3</text></g>
  </svg>;
}

const Metric = ({ value, label, tone = "cyan" }: { value: string; label: string; tone?: string }) => <div className={`report-metric ${tone}`}><strong>{value}</strong><span>{label}</span></div>;

export function ClinicalReportPrototype() {
  return <main className="report-prototype">
    <header className="report-toolbar">
      <a href="./" aria-label="Voltar ao Heryx"><ArrowLeft size={17}/><span>Voltar ao Heryx</span></a>
      <div className="report-toolbar-title"><span className="report-logo"><Dna/></span><span><strong>Relatório clínico</strong><small>PRÉ-VISUALIZAÇÃO · HRYX-024</small></span></div>
      <div className="report-toolbar-actions"><button><Printer/>Imprimir</button><button className="primary"><Download/>Exportar PDF</button></div>
    </header>

    <section className="report-viewer" aria-label="Prévia do relatório clínico">
      <article className="clinical-page cover-page">
        <div className="cover-orbit cover-orbit-one"/><div className="cover-orbit cover-orbit-two"/>
        <header className="page-brand"><span className="report-logo"><Dna/></span><span><b>Heryx</b><small>HEREDITARY ANALYTICS</small></span><i>RELATÓRIO CLÍNICO · 01</i></header>
        <section className="cover-heading"><span className="eyebrow">ANÁLISE DE HEREDOGRAMA</span><h1>Relatório de<br/><em>história familiar</em></h1><p>Documento de apoio à avaliação genética, organização fenotípica e interpretação de vínculos familiares.</p><span className="cover-edition">EDIÇÃO CLÍNICA · 2026</span></section>
        <div className="case-identity"><div><small>IDENTIFICAÇÃO DO CASO</small><strong>Família HRYX-024</strong><span>Código do estudo · RPS-2026-024</span></div><div><small>DATA DE EMISSÃO</small><strong>07 NOV 2026</strong><span>Versão 1.0</span></div><div><small>STATUS</small><strong className="status-ready"><CheckCircle2/>Revisado</strong><span>Dados armazenados localmente</span></div></div>
        <section className="cover-pedigree"><div className="section-heading"><span><Dna/>Visão familiar</span><small>3 GERAÇÕES · 9 INDIVÍDUOS</small></div><MiniPedigree/></section>
        <div className="cover-summary"><div><Activity/><span><small>HIPÓTESE EM AVALIAÇÃO</small><strong>Padrão de herança autossômica dominante</strong></span></div><p>O heredograma demonstra agregação familiar de manifestação neuromuscular, com indivíduos afetados em gerações sucessivas.</p></div>
        <footer className="page-footer"><span><ShieldCheck/>Documento confidencial · uso clínico</span><span>HERYX · 01 / 06</span></footer>
      </article>

      <article className="clinical-page content-page">
        <header className="page-brand"><span className="report-logo"><Dna/></span><span><b>Heryx</b><small>HEREDITARY ANALYTICS</small></span><i>FAMÍLIA HRYX-024</i></header>
        <section className="page-title"><span className="eyebrow">01 · SÍNTESE CLÍNICA</span><h2>Resumo do caso</h2><p>Visão consolidada das informações registradas no projeto.</p></section>
        <section className="metrics-row"><Metric value="09" label="Indivíduos"/><Metric value="03" label="Gerações"/><Metric value="04" label="Fenótipos HPO" tone="violet"/><Metric value="02" label="Afetados" tone="coral"/></section>
        <section className="report-grid">
          <div className="report-card clinical-note"><div className="section-heading"><span><FileText/>Observação clínica</span><small>REGISTRO DO CASO</small></div><p>Probando com início de fraqueza muscular proximal aos 14 anos, progressão lenta e relato de quadro semelhante no ramo materno. Sem consanguinidade informada.</p><div className="note-meta"><span>Última atualização</span><b>07 nov 2026 · 14:32</b></div></div>
          <div className="report-card interpretation"><div className="section-heading"><span><Activity/>Interpretação</span><small>RESULTADO PRELIMINAR</small></div><strong>Compatível com transmissão vertical</strong><p>A distribuição entre gerações sugere priorizar hipóteses autossômicas dominantes, considerando penetrância variável.</p><span className="confidence"><i style={{width:"78%"}}/>Confiança moderada · 78%</span></div>
        </section>
        <section className="phenotype-section"><div className="section-heading"><span><Dna/>Fenótipos registrados</span><small>HUMAN PHENOTYPE ONTOLOGY</small></div><table><thead><tr><th>Termo HPO</th><th>Descrição</th><th>Indivíduos</th><th>Registro</th></tr></thead><tbody><tr><td><b>HP:0003324</b></td><td>Fraqueza muscular geral</td><td><span className="person-chip">III-2</span><span className="person-chip">II-2</span></td><td><span className="confirmed">Confirmado</span></td></tr><tr><td><b>HP:0003701</b></td><td>Atrofia muscular proximal</td><td><span className="person-chip">III-2</span></td><td><span className="confirmed">Confirmado</span></td></tr><tr><td><b>HP:0001250</b></td><td>Convulsões</td><td><span className="person-chip">II-2</span></td><td><span className="pending">Referido</span></td></tr><tr><td><b>HP:0001263</b></td><td>Atraso global do desenvolvimento</td><td><span className="person-chip">III-2</span></td><td><span className="pending">Em revisão</span></td></tr></tbody></table></section>
        <section className="report-alert"><ShieldCheck/><span><strong>Validação do projeto concluída</strong><small>Vínculos familiares consistentes. Dois registros clínicos permanecem pendentes de confirmação documental.</small></span></section>
        <footer className="page-footer"><span>Gerado localmente pelo Heryx · hereditary analytics</span><span>HERYX · 02 / 06</span></footer>
      </article>

      <article className="clinical-page content-page">
        <header className="page-brand"><span className="report-logo"><Dna/></span><span><b>Heryx</b><small>HEREDITARY ANALYTICS</small></span><i>FAMÍLIA HRYX-024</i></header>
        <section className="page-title"><span className="eyebrow">02 · ESTRUTURA FAMILIAR</span><h2>Heredograma completo</h2><p>Representação clínica da família fictícia em três gerações.</p></section>
        <section className="full-pedigree-card"><div className="generation-key"><span>I</span><span>II</span><span>III</span></div><MiniPedigree detailed/></section>
        <section className="legend-panel"><strong>Legenda</strong><span><i className="legend-symbol square"/>Masculino</span><span><i className="legend-symbol circle"/>Feminino</span><span><i className="legend-symbol affected"/>Fenótipo presente</span><span><i className="legend-arrow">↗</i>Probando</span></section>
        <section className="family-history-block"><div className="section-heading"><span><FileText/>História familiar</span><small>SÍNTESE NARRATIVA</small></div><p>A família HRYX-024 foi encaminhada para avaliação após identificação de fraqueza muscular progressiva no probando III-2. A mãe (II-2) refere manifestações semelhantes desde a terceira década de vida. A avó materna (I-4) teria apresentado limitação funcional tardia, sem documentação disponível. Os demais familiares são assintomáticos conforme relato.</p><div className="history-facts"><span><b>Consanguinidade</b>Não informada</span><span><b>Ancestralidade</b>Brasileira, não especificada</span><span><b>Ramo prioritário</b>Materno</span></div></section>
        <section className="report-callout"><Activity/><div><strong>Leitura do padrão familiar</strong><p>Afetados em gerações sucessivas, ambos os sexos representados e possível transmissão vertical. A hipótese permanece preliminar e deve ser correlacionada com avaliação clínica e molecular.</p></div></section>
        <footer className="page-footer"><span>Representação fictícia para demonstração do modelo</span><span>HERYX · 03 / 06</span></footer>
      </article>

      <article className="clinical-page content-page">
        <header className="page-brand"><span className="report-logo"><Dna/></span><span><b>Heryx</b><small>HEREDITARY ANALYTICS</small></span><i>FAMÍLIA HRYX-024</i></header>
        <section className="page-title"><span className="eyebrow">03 · INDIVÍDUOS</span><h2>Registros clínicos</h2><p>Dados essenciais dos familiares mais relevantes para a investigação.</p></section>
        <section className="patient-profile proband-profile"><header><span className="profile-avatar"><UserRound/></span><div><small>PROBANDO · III-2</small><h3>Indivíduo HRYX-III-02</h3><p>Masculino · 19 anos · fenótipo presente</p></div><span className="profile-status">EM AVALIAÇÃO</span></header><div className="profile-grid"><div><small>INÍCIO DOS SINTOMAS</small><strong>14 anos</strong></div><div><small>CONDIÇÃO PRINCIPAL</small><strong>Fraqueza muscular proximal</strong></div><div><small>SEGUIMENTO</small><strong>Neurologia e genética</strong></div><div><small>TESTE MOLECULAR</small><strong>Não realizado</strong></div></div><p className="profile-note">Relata dificuldade progressiva para subir escadas e levantar-se de assentos baixos. Exame inicial sugere redução de força em cinturas pélvica e escapular.</p></section>
        <section className="relative-cards"><article><header><span className="profile-avatar small"><UserRound/></span><span><small>II-2 · MÃE</small><strong>Indivíduo HRYX-II-02</strong></span><i className="affected-dot"/></header><dl><div><dt>Idade</dt><dd>43 anos</dd></div><div><dt>Fenótipo</dt><dd>Presente</dd></div><div><dt>Início</dt><dd>28 anos</dd></div></dl><p>Fraqueza proximal leve e elevação de CK referida em prontuário externo.</p></article><article><header><span className="profile-avatar small"><UserRound/></span><span><small>I-4 · AVÓ MATERNA</small><strong>Indivíduo HRYX-I-04</strong></span><i className="uncertain-dot"/></header><dl><div><dt>Idade</dt><dd>71 anos</dd></div><div><dt>Fenótipo</dt><dd>Incerto</dd></div><div><dt>Início</dt><dd>Após 50 anos</dd></div></dl><p>História referida de limitação para marcha. Ausência de registros clínicos comprobatórios.</p></article></section>
        <section className="clinical-table-wrap"><div className="section-heading"><span><Stethoscope/>Comparação clínica</span><small>INDIVÍDUOS PRIORITÁRIOS</small></div><table><thead><tr><th>Característica</th><th>III-2</th><th>II-2</th><th>I-4</th></tr></thead><tbody><tr><td>Fraqueza proximal</td><td>Presente</td><td>Presente</td><td>Referida</td></tr><tr><td>Atrofia muscular</td><td>Presente</td><td>Ausente</td><td>Não informado</td></tr><tr><td>Convulsões</td><td>Ausente</td><td>Referida</td><td>Não informado</td></tr><tr><td>CK elevada</td><td>Em análise</td><td>Referida</td><td>Não informado</td></tr></tbody></table></section>
        <footer className="page-footer"><span>Identificadores anonimizados para proteção da família</span><span>HERYX · 04 / 06</span></footer>
      </article>

      <article className="clinical-page content-page">
        <header className="page-brand"><span className="report-logo"><Dna/></span><span><b>Heryx</b><small>HEREDITARY ANALYTICS</small></span><i>FAMÍLIA HRYX-024</i></header>
        <section className="page-title"><span className="eyebrow">04 · EVOLUÇÃO E INTERPRETAÇÃO</span><h2>Linha do tempo clínica</h2><p>Eventos relevantes registrados durante a investigação fictícia.</p></section>
        <section className="timeline"><article><time>2021<small>14 ANOS</small></time><i/><div><strong>Primeiros sinais</strong><p>Dificuldade para acompanhar atividades esportivas e subir escadas.</p></div></article><article><time>2023<small>16 ANOS</small></time><i/><div><strong>Avaliação neurológica</strong><p>Redução de força proximal; fisioterapia motora iniciada.</p></div></article><article><time>2025<small>18 ANOS</small></time><i/><div><strong>História familiar ampliada</strong><p>Identificação de manifestação semelhante na mãe e possível caso na avó materna.</p></div></article><article><time>2026<small>19 ANOS</small></time><i/><div><strong>Encaminhamento para genética</strong><p>Heredograma estruturado, termos HPO registrados e investigação molecular proposta.</p></div></article></section>
        <section className="interpretation-matrix"><div className="section-heading"><span><Activity/>Análise do padrão</span><small>HIPÓTESES PRIORIZADAS</small></div><article><span>01</span><div><strong>Herança autossômica dominante</strong><p>Hipótese principal: transmissão vertical e ambos os sexos potencialmente afetados.</p></div><b>ALTA</b></article><article><span>02</span><div><strong>Herança ligada ao X</strong><p>Hipótese alternativa a depender da confirmação fenotípica no ramo materno.</p></div><b className="medium">MODERADA</b></article><article><span>03</span><div><strong>Fenocópia ou etiologia multifatorial</strong><p>Considerar se os achados clínicos não forem molecularmente concordantes.</p></div><b className="low">BAIXA</b></article></section>
        <section className="pending-panel"><AlertTriangle/><div><strong>Pendências antes da conclusão</strong><ul><li>Confirmar documentação clínica da avó materna I-4.</li><li>Revisar resultado de CK da mãe II-2.</li><li>Realizar avaliação cardiológica e respiratória do probando.</li><li>Discutir estratégia de teste molecular em aconselhamento genético.</li></ul></div></section>
        <footer className="page-footer"><span>Interpretação computacional não substitui avaliação especializada</span><span>HERYX · 05 / 06</span></footer>
      </article>

      <article className="clinical-page content-page">
        <header className="page-brand"><span className="report-logo"><Dna/></span><span><b>Heryx</b><small>HEREDITARY ANALYTICS</small></span><i>FAMÍLIA HRYX-024</i></header>
        <section className="page-title"><span className="eyebrow">05 · MÉTODOS E REFERÊNCIAS</span><h2>Base da análise</h2><p>Critérios, limitações e fontes utilizadas na elaboração do relatório.</p></section>
        <section className="method-list"><article><span>01</span><div><strong>Construção do heredograma</strong><p>Estrutura familiar organizada em três gerações conforme convenções padronizadas de nomenclatura e representação gráfica.</p></div></article><article><span>02</span><div><strong>Descrição fenotípica</strong><p>Achados codificados com termos da Human Phenotype Ontology, versão consultada em novembro de 2026.</p></div></article><article><span>03</span><div><strong>Inferência do padrão de herança</strong><p>Priorização baseada exclusivamente na distribuição familiar registrada e sujeita à confirmação clínica e molecular.</p></div></article></section>
        <section className="limitations"><div className="section-heading"><span><ShieldCheck/>Limitações</span><small>LEITURA OBRIGATÓRIA</small></div><ul><li>Informações familiares podem conter imprecisões de memória ou registros incompletos.</li><li>Ausência de manifestação não exclui penetrância reduzida ou início tardio.</li><li>Este relatório não estabelece diagnóstico e não substitui aconselhamento genético.</li><li>As hipóteses devem ser revistas quando novos dados forem adicionados.</li></ul></section>
        <section className="references"><div className="section-heading"><span><BookOpen/>Literatura essencial</span><small>REFERÊNCIAS</small></div><ol><li>Richards S, et al. Standards and guidelines for the interpretation of sequence variants. <em>Genet Med.</em> 2015.</li><li>Köhler S, et al. The Human Phenotype Ontology in 2021. <em>Nucleic Acids Res.</em> 2021.</li><li>Bennett RL, et al. Standardized human pedigree nomenclature: update and assessment. <em>J Genet Couns.</em> 2008.</li></ol></section>
        <section className="signature-block"><div><small>RESPONSÁVEL PELO REGISTRO</small><span/><strong>Nome e registro profissional</strong></div><div><small>DATA DA REVISÃO</small><span/><strong>____ / ____ / ______</strong></div></section>
        <section className="report-disclaimer"><Clock3/><p><strong>Documento demonstrativo.</strong> Todos os nomes, identificadores e dados clínicos apresentados neste modelo são fictícios e foram criados exclusivamente para visualização do relatório Heryx.</p></section>
        <footer className="page-footer"><span><ShieldCheck/>Processamento local · privacidade por padrão</span><span>HERYX · 06 / 06</span></footer>
      </article>
    </section>
  </main>;
}
