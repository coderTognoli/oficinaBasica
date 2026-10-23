# DOCUMENTAÇÃO DE SOFTWARE - ANEXO 1
## SISTEMA DE GESTÃO E AGENDAMENTO DE SERVIÇOS PARA OFICINA MECÂNICA (SAEP)

---

### 1. IDENTIFICAÇÃO DO PROJETO
- **Nome do Sistema:** AutoMecânica Pro - Sistema Integrado de Gestão de Oficina
- **Versão:** 1.0.0 (Release SAEP)
- **Data:** Outubro de 2026
- **Tecnologias Utilizadas:** 
  - Backend: Python 3.10+ / Flask 3.0
  - Banco de Dados: MySQL 8.0 (Engine InnoDB)
  - Criptografia: Bcrypt (Hash de senhas e proteção de CPF conforme LGPD)
  - Frontend: HTML5, CSS3 puro, JavaScript Puro (Vanilla JS)
  - Controle de Sessão: Cookies HTTP-Only com Expiração Temporal

---

### 2. VISÃO GERAL E JUSTIFICATIVA
A ausência de um sistema informatizado na oficina mecânica gerava perdas financeiras, extravio de horários de atendimento, duplicidade no cadastro de clientes e veículos, além de sérios riscos de autuações pela LGPD (Lei Geral de Proteção de Dados - Lei nº 13.709/2018) devido ao armazenamento desprotegido de dados sensíveis como o CPF.
A presente solução automatiza o fluxo operacional de atendimento, armazena hashes Bcrypt de CPFs e senhas (sem possibilidade de recuperar o valor original), implementa controle estrito de expiração de sessão e garante a rastreabilidade integral entre clientes, veículos e serviços agendados.

---

### 3. REQUISITOS FUNCIONAIS (RF)

| Código | Nome do Requisito | Descrição Detalhada | Prioridade |
|---|---|---|---|
| **RF01** | Autenticação de Usuários | O sistema deve permitir login de usuários com login e senha. Deve validar credenciais incorretas e exibir mensagem de erro explícita. | Alta |
| **RF02** | Controle de Expiração de Sessão | A sessão do usuário autenticado deve possuir tempo limite de inatividade (15 minutos), exigindo novo login após esse período. | Alta |
| **RF03** | Funcionalidade Principal (Dashboard) | Deve exibir no cabeçalho o nome do usuário logado, atalhos claros para todos os recursos e opção visível de encerramento da sessão (logout). | Alta |
| **RF04** | Cadastro e Proteção de Clientes | Permitir cadastrar clientes. O CPF deve ser validado para conter exatamente 11 dígitos numéricos e deve ser armazenado com criptografia Bcrypt no BD. | Alta |
| **RF05** | Busca de Clientes por Termo | Permitir ao usuário inserir um termo de busca e, após confirmação, exibir a listagem atualizada correspondente. | Média |
| **RF06** | Edição de Dados do Cliente | Permitir editar dados cadastrais de clientes previamente cadastrados e salvar as alterações no banco de dados. | Alta |
| **RF07** | Cadastro de Veículos com Associação | Permitir o cadastro de veículos associando-os obrigatoriamente a um cliente previamente cadastrado. | Alta |
| **RF08** | Listagem de Agendamentos Ordenada | Exibir os serviços agendados ordenados cronologicamente por data (ASC), exibindo todos os dados do cliente e do veículo relacionado. | Alta |
| **RF09** | Atualização de Data de Agendamento | Permitir alterar a data e horário de um agendamento existente e persistir a alteração no banco de dados. | Alta |

---

### 4. REQUISITOS NÃO FUNCIONAIS (RNF)

| Código | Categoria | Descrição |
|---|---|---|
| **RNF01** | Segurança & LGPD | O CPF do cliente e as senhas de usuários devem ser protegidos com algoritmo criptográfico de hash seguro (Bcrypt com Salt), prevenindo vazamento de dados pessoais. |
| **RNF02** | Modularidade | O código fonte backend deve ser estritamente modularizado em arquivos especializados (app.py, clientes.py, veiculos.py, agendamento.py, autenticacao.py, rotas.py). |
| **RNF03** | Interface Pura | Frontend construído sem dependência de frameworks externos pesados (HTML5 semântico, CSS3 e JavaScript puro). |
| **RNF04** | Confiabilidade do BD | O banco de dados deve utilizar MySQL com mecanismo InnoDB, garantindo transações ACID e integridade referencial via Foreign Keys com CASCADE. |
| **RNF05** | Usabilidade | Feedback visual instantâneo para erros de validação, confirmações de exclusão e mensagens de sucesso via flash messages. |

---

### 5. REGRAS DE NEGÓCIO (RN)

- **RN01 (Massa Inicial de Dados):** O script de banco de dados (`saep_db.sql`) deve conter pelo menos três registros válidos para todas as tabelas criadas.
- **RN02 (Validação de Falha de Login):** Em caso de usuário inexistente ou senha incorreta, o sistema deve impedir o acesso e apresentar alerta explícito.
- **RN03 (Criptografia do CPF):** O CPF não pode ser armazenado em texto legível no banco de dados sem proteção criptográfica Bcrypt, atendendo à LGPD.
- **RN04 (Validação Sintética de CPF):** Validar apenas a quantidade de 11 dígitos numéricos do CPF, sem exigência de validação de dígito verificador matemático.
- **RN05 (Associação Obrigatória de Veículo):** Não é permitido cadastrar um veículo sem associá-lo a um cliente existente no sistema.
- **RN06 (Visibilidade Total no Agendamento):** A listagem de agendamentos deve trazer os dados do cliente (Nome, Telefone, E-mail, Endereço), do veículo (Placa, Modelo, Marca, Ano e Cor) e do serviço, ordenados por data.
- **RN07 (Reprogramação de Data):** Apenas a data/horário do agendamento pode ser atualizada de forma isolada na rotina de reagendamento.

---

### 6. DICIONÁRIO DE DADOS (MODELO FÍSICO)

#### Tabela: `usuarios`
- `id` INT AUTO_INCREMENT PRIMARY KEY
- `nome` VARCHAR(100) NOT NULL
- `login` VARCHAR(50) NOT NULL UNIQUE
- `senha_hash` CHAR(60) NOT NULL (Hash Bcrypt)
- `cargo` VARCHAR(60) NOT NULL
- `ativo` BOOLEAN NOT NULL DEFAULT TRUE
- `criado_em` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### Tabela: `clientes`
- `id` INT AUTO_INCREMENT PRIMARY KEY
- `nome` VARCHAR(120) NOT NULL
- `cpf_hash` CHAR(60) NOT NULL (Hash Bcrypt; o CPF original não é recuperável)
- `telefone` VARCHAR(20)
- `email` VARCHAR(120)
- `endereco` VARCHAR(200)
- `criado_em` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### Tabela: `veiculos`
- `id` INT AUTO_INCREMENT PRIMARY KEY
- `cliente_id` INT NOT NULL (FK -> clientes.id)
- `placa` VARCHAR(7) NOT NULL UNIQUE
- `marca` VARCHAR(50) NOT NULL
- `modelo` VARCHAR(50) NOT NULL
- `ano` SMALLINT NOT NULL
- `cor` VARCHAR(30)

#### Tabela: `agendamentos`
- `id` INT AUTO_INCREMENT PRIMARY KEY
- `veiculo_id` INT NOT NULL (FK -> veiculos.id)
- `servico_id` INT NOT NULL (FK -> servicos.id)
- `data_agendamento` DATETIME NOT NULL
- `status` ENUM('AGENDADO', 'EM_ANDAMENTO', 'CONCLUIDO', 'CANCELADO') NOT NULL DEFAULT 'AGENDADO'
- `observacao` VARCHAR(255)

#### Tabela: `servicos`
- `id` INT AUTO_INCREMENT PRIMARY KEY
- `descricao` VARCHAR(100) NOT NULL
- `valor` DECIMAL(10,2) NOT NULL

---
Documento elaborado em conformidade com o padrão de avaliação técnica SAEP / SENAI.
