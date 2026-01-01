function switch_to_txt2img(){
    gradioApp().querySelector('#tabs').querySelectorAll('button')[0].click();
}

// Tooltips
var prompt_architect_titles = {
    "Temperatura": "Più alta = più creativo ma caotico. Più bassa = più coerente.",
    "Lunghezza Massima": "Quante parole può scrivere il modello.",
    "Genera Prompts ✨": "Avvia l'intelligenza artificiale per creare i tuoi prompt."
};

onUiUpdate(function(){
    gradioApp().querySelectorAll('span, button').forEach(function(el){
        let tooltip = prompt_architect_titles[el.textContent];
        if(tooltip) el.title = tooltip;
    });
});