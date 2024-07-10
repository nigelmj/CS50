document.addEventListener('DOMContentLoaded', function() {

    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', () => compose_email('','',''));
	document.querySelector('#compose-form').onsubmit = send_mail

    // By default, load the inbox
	load_mailbox('inbox')
});

function compose_email(recip, sub, body) {

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#maildetails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';

    // Clear out composition fields
    document.querySelector('#compose-recipients').value = recip;
    document.querySelector('#compose-subject').value = sub;
    document.querySelector('#compose-body').value = body;
}

function send_mail() {

	const recipients = document.querySelector('#compose-recipients').value;
	const subject = document.querySelector('#compose-subject').value;
	const body = document.querySelector('#compose-body').value;

	fetch('/emails', {
		method: 'POST',
		body: JSON.stringify({
			recipients: recipients,
			subject: subject,
			body: body
		})
	})
	.then(response => response.json())
	.then(result => {
		load_mailbox('sent')
	})

	return false;

}

function load_mailbox(mailbox) {
  
	// Show the mailbox and hide other views
	document.querySelector('#emails-view').style.display = 'block';
	document.querySelector('#compose-view').style.display = 'none';
	document.querySelector('#maildetails-view').style.display = 'none';

	// Show the mailbox name
	document.querySelector('#mailboxname').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
	document.querySelector('#mailbox').innerHTML = "";

	fetch(`/emails/${mailbox}`)
	.then(response => response.json())
	.then(emails => {
		emails.forEach(function(email) {
			show_mails(email,mailbox)
		});
	})
}

function show_mails(email, mailbox) {

	const id = email.id
	var address = email.sender
	if (mailbox === 'sent') {
		var address = 'To: ' + email.recipients
	}

	const ediv = document.createElement('div');
	ediv.id = `mail${id}`
	ediv.className = 'mail'
	ediv.innerHTML = `<div class='address'>${address}</div><div class='subject'>${email.subject}</div> <div class='date'>${email.timestamp}</div>`;

	if (email.read) {
		ediv.classList.add("read")
	}
	document.querySelector('#mailbox').append(ediv);
	document.querySelector(`#mail${id}`).addEventListener('click', () => mail_details(id, mailbox));
}

function mail_details(email_id, mailbox) {

	document.querySelector('#emails-view').style.display = 'none';
	document.querySelector('#compose-view').style.display = 'none';

	document.querySelector('#maildetails-view').style.display = "block";
	document.querySelector('#maildetails-view').innerHTML = "<div id='head'></div><hr><div id='body'></div>";

	fetch(`/emails/${email_id}`)
	.then(response => response.json())
	.then(email => {
		const sender = email.sender
		const recipients = email.recipients
		const subject = email.subject
		const timestamp = email.timestamp
		const body_info = email.body
		const state = email.archived

		if (!email.read) {
			fetch(`/emails/${email_id}`, {
				method: 'PUT',
				body: JSON.stringify({
					read: true
				})
			})
		} 

		var text = "Archive"
		if (state) {
			var text = "Unarchive"
		} 

		const head = document.querySelector("#head")
		const body = document.querySelector('#body')
		
		head.innerHTML = `
			<div><h6 style="display:inline; font-weight:700;">From: </h6>${sender}</div>
			<div><h6 style="display:inline; font-weight:700;">To: </h6>${recipients}</div>
			<div><h6 style="display:inline; font-weight:700;">Subject: </h6>${subject}</div>
			<div><h6 style="display:inline; font-weight:700;">Timestamp: </h6>${timestamp}</div>
			<div id="action-btns" style="white-space:nowrap;">
				<button style="display:inline-block;" id="archive-btn" class="btn btn-sm btn-outline-primary">${text}</button>
				<button style="display:inline-block;" id="reply-btn" class="btn btn-sm btn-outline-primary">Reply</button>
			</div>
		`
		body.innerHTML = `<div style="white-space: pre;">${body_info}</div>`

		if (mailbox !== 'sent') {
			const arch_btn = document.querySelector("#archive-btn")
			const reply_btn = document.querySelector("#reply-btn")
			reply_btn.onclick = function() {
				reply(email_id)
			}
			arch_btn.style.display = "inline-block"
			arch_btn.onclick = function() {
				archive(email_id, state)
			}
		} else {
			document.querySelector("#action-btns").style.display = "none"
		}
	})

	function archive(email_id, state) {

		fetch(`/emails/${email_id}`, {
			method: 'PUT',
			body: JSON.stringify({
				archived: !state
			})
		})
		.then(result => {
			load_mailbox('inbox')
		})

	}

	function reply(email_id) {

		fetch(`/emails/${email_id}`)
		.then(response => response.json())
		.then(email => {
			const sender = email.sender
			var subject = email.subject
			const timestamp = email.timestamp
			const body_info = email.body

			if (subject.slice(0,4) !== 'Re: ') {
				var subject = 'Re: ' + subject
			}
			const body = `"On ${timestamp} ${sender} wrote: ${body_info}"`
			compose_email(sender, subject, body)
		})
	}
}

