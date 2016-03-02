/*
 * Vigiboard
 *
 * Copyright (C) 2009-2016 CS-SI
 */

// Appelé au chargement de la page
window.addEvent('domready', function (){

    // Ajout de l'auto-complétion sur le champ 'host'
    host_autocompleter = add_autocompleter(
        $('host'), 'host', app_path + '/autocomplete/host');

    // Ajout de l'auto-complétion sur le champ 'service'
    service_autocompleter = add_autocompleter(
        $('service'), 'service', app_path + '/autocomplete/service',
        {'host': $('host').get('value')}, false);

    // On lie l'auto-complétion sur le service à celle concernant l'hôte :
    // lorsque le champ 'host' est modifié, on vide le champ 'service', et on
    // modifie le paramètre 'host' de l'auto-compléteur du service
    host_autocompleter.addEvent("selection", function(element, selected, value, input) {
        $('service').set('value','');
        service_autocompleter.options.postData.set('host', value);
    });

    // En fonction du remplissage du champ 'service', on adapte la nature du
    // champ 'states'
    adapt_states_field();
    service_autocompleter.addEvent("selection", function(event) {
        adapt_states_field();
    });
    $('service').addEvent("change", function(event) {
        adapt_states_field();
    });

    // On appelle la fonction 'submit_form' lorsque l'utilisateur valide le
    // formulaire
    $('silence_form').addEvent("submit", function(event) {
        submit_form();
    });

    // On place le focus sur le champ 'host' pour faciliter la saisie
    $('host').setAttribute('tabIndex', 0);
    $('host').focus();
});

// Fonction ajoutant l'auto-complétion sur un champ du formulaire
function add_autocompleter(elem, varname, url, postData, forceSelect) {
    if (!$defined(forceSelect))
        forceSelect = true;
    var autocompleter = new Autocompleter.Request.VigiloJSON(elem, url, {
        'minLength': 1, // Attendre 1 caractère avant l'envoi de la requête
        'selectMode': 'pick',
        'postVar' : varname,
        'zIndex' : 2000,    // Limite le risque qu'un dialogue ne masque
                            // l'encadré d'auto-complétion.
        'overflow': true, // Overflow for more entries
        'postData' : new Hash({'partial': true}).combine(postData),
        'forceSelect' : forceSelect
    });
    elem.store("autocompleter", autocompleter);
    return autocompleter;
}

// Fonction adaptant le champ "states" du formulaire en fonction de la nature
// du supitem sur lequel porte la règle de mise en silence
function adapt_states_field() {
    // Si le champ 'service' est vide, on cache les états spécifiques aux
    // services et on affiche les états d'hôtes
    if ($('service').get('value') === '') {
        $('service_states').hide();
        $('host_states').show();
    // Si le champ 'service' n'est pas vide, on affiche les états spécifiques
    // aux services et on masque les états d'hôtes
    } else {
        $('service_states').show();
        $('host_states').hide();
    }

}

// Fonction appelée suite à la validation du formulaire
function submit_form() {
    // Traitement des règles portant sur les hôtes
    if ($('service').get('value') === '') {
        $('states').set('value', $$('#host_states input').get('value')[0]);
        $('host_states').destroy();
        $('service_states').destroy();
    // Traitement des règles portant sur les services
    } else {
        $('states').set('value', $$('#service_states select').get('value'));
        $('host_states').destroy();
        $('service_states').destroy();
    }
    return true;
}
