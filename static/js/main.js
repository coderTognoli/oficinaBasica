// Funções de manipulação do Frontend em JavaScript Puro

function abrirModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function fecharModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Fecha modal clicando fora da caixa
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Função para abrir modal de edição de cliente preenchendo os campos
function abrirModalEditar(id, nome, telefone, email, endereco) {
    const form = document.getElementById('formEditarCliente');
    if (form) {
        form.action = '/clientes/editar/' + id;
        document.getElementById('edit_nome').value = nome;
        document.getElementById('edit_telefone').value = telefone;
        document.getElementById('edit_email').value = email;
        document.getElementById('edit_endereco').value = endereco;
        abrirModal('modalEditarCliente');
    }
}

// Função para abrir modal de edição de veículo preenchendo os campos
function abrirModalEditarVeiculo(id, clienteId, placa, marca, modelo, ano, cor) {
    const form = document.getElementById('formEditarVeiculo');
    if (form) {
        form.action = '/veiculos/editar/' + id;
        document.getElementById('edit_veiculo_cliente_id').value = clienteId;
        document.getElementById('edit_veiculo_placa').value = placa;
        document.getElementById('edit_veiculo_marca').value = marca;
        document.getElementById('edit_veiculo_modelo').value = modelo;
        document.getElementById('edit_veiculo_ano').value = ano;
        document.getElementById('edit_veiculo_cor').value = cor || '';
        abrirModal('modalEditarVeiculo');
    }
}

// Função para abrir modal de atualização da data do agendamento
function abrirModalAtualizarData(agendamentoId, dataAtual) {
    const form = document.getElementById('formAtualizarData');
    if (form) {
        form.action = '/agendamentos/atualizar-data/' + agendamentoId;
        // Se a data já contiver formato compatível, preenche
        if (dataAtual) {
            const formatted = dataAtual.replace(' ', 'T').substring(0, 16);
            const input = document.getElementById('nova_data_agendamento');
            if (input) input.value = formatted;
        }
        abrirModal('modalAtualizarData');
    }
}
