# Controlador DataLab

Plano de controle do portfólio autônomo de Ciência de Dados da organização **DatalabMp**.

## Missão

Criar e evoluir projetos públicos e reproduzíveis de Ciência de Dados baseados em dados reais, com ênfase em interpretação, rigor estatístico, dashboards, testes, segurança e monitoramento transparente.

## Regras não negociáveis

- Proprietário GitHub autorizado: somente `DatalabMp`.
- Nunca modificar repositórios fora de `DatalabMp`.
- Agentes especialistas não enviam código diretamente.
- Somente o Executor pode escrever após a aprovação dos controles obrigatórios.
- Nenhum commit vazio, artificial ou sem significado.
- Mensagens de commit devem ser escritas em português do Brasil.
- O orçamento externo de IA/API é limitado rigidamente a **USD 0,00**.
- Fallback para modelos pagos é proibido.
- Se todas as opções gratuitas ou locais estiverem indisponíveis, a execução é pausada em vez de gerar custo.
- Conclusões analíticas devem distinguir associação de causalidade e documentar limitações.

## Agentes especialistas

1. Requisitos
2. Arquitetura
3. Dados e Qualidade
4. Estatística
5. Modelagem
6. Visualização
7. Qualidade e Testes
8. Segurança
9. Revisor Independente
10. Executor — único papel autorizado a escrever

## Projetos planejados

- Análise de Segurança Viária no Brasil — PRF
- Monitor Econômico do Brasil — Banco Central do Brasil
- Análise do ENEM — INEP
- Observatório de População e Trabalho do Brasil — IBGE
- Análise de Saúde do SUS — DATASUS
- Análise da Agricultura Brasileira — IBGE/PAM

## Monitoramento

A **Central de Operações e Orquestração** é publicada pelo GitHub Pages e reconstruída a partir do estado do controlador. Ela mostra progresso dos projetos, estado dos agentes, controles de validação, falhas, commits, agenda operacional, provedores, tokens quando reportados e custo externo confirmado.

Painel: `https://datalabmp.github.io/datalab-controller/`

## Fábrica de Projetos

O controlador possui uma fábrica protegida de repositórios para a cadência de novos projetos a cada 72 horas. A autenticação é feita por uma GitHub App dedicada instalada exclusivamente em `DatalabMp`.

A fábrica pode criar somente repositórios públicos dentro de `DatalabMp`, recusa adoção automática de repositórios preexistentes, inicializa manifesto DataLab, CI, testes, documentação e GitHub Pages, e registra o novo projeto no estado do controlador.

## Idioma operacional

Todo conteúdo visível ao usuário, documentação operacional, eventos, nomes exibidos no dashboard e mensagens de commit devem ser escritos em **português do Brasil**. Identificadores técnicos internos podem permanecer em inglês quando sua alteração puder comprometer compatibilidade ou lógica existente.

## Estado atual

- Fundação do controlador: ativa
- Integração contínua: operacional
- Central de Operações: publicada no GitHub Pages
- Fábrica de Projetos: operacional
- GitHub App dedicada: operacional
- Primeiro projeto gerenciado: `DatalabMp/brazil-road-safety`
- Custo externo de IA/API permitido: USD 0,00
