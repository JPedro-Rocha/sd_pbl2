function atualizarTemporizador(event) {

    let id = event.target.id
    let form = document.getElementById("form" + id).value
    console.log(form)
    let horario = document.getElementById("horario" + id).value
    console.log(horario)
    let estado = document.getElementById("estado" + id).value
    console.log(estado)

    $.ajax({
        type: "POST",
        url: "/IoT/atualizar_temporizador/" + id + "/",
        // data: {
        //     horario: horario,
        //     estado: estado
        // },
        success: function(response) {
            console.log(response)
        },
        error: function(error) {
            console.log(error)
        }
    })
}

$(document).ready(function() {
    $(".form-temporizador").submit(atualizarTemporizador(event));
    // var el = document.getElementById('fora');
    // el.addEventListener('click', function(e) {
    //     alert(e.target.id);
    // });
});