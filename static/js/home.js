window.addEvent('domready', function() {
	'use strict';

	$$('form')[0].addEvent('submit', function(e) {
		e.preventDefault();
		var form = e.target;
		var character = form.getElement('input[name="char"]').get('value');
		character = character.replace(' ', '_');
		window.location.pathname = '/skillcheck/' + character;
	});
});
