document.addEventListener("DOMContentLoaded", () => {

    if (document.querySelector("#sendpost-form")) {
        document.querySelector("#sendpost-form").onsubmit = new_post
    }

    if (document.querySelectorAll(".edit-link")) {
        document.querySelectorAll(".edit-link").forEach(link => {
            link.onclick = () => {
                edit_post(link.dataset.id);
                return false;
            }
        })
    }

    if (document.querySelectorAll(".btn-like")) {
        document.querySelectorAll(".btn-like").forEach(button => {
            button.onclick = () => {
                like(button.dataset.id, button.dataset.like_status)
            }
        })
    }

    if (document.querySelectorAll(".btn-follow")) {
        document.querySelectorAll(".btn-follow").forEach(button => {
            button.onclick = () => {
                follow(button.dataset.username, button.dataset.follow_status)
            }
        })
    }
});

function new_post() {

	const post = document.querySelector('#post_text').value;
	fetch('/newpost', {
		method: 'POST',
		body: JSON.stringify({
			post: post
		})
	})

	.then(response => response.json())
	.then(result => {
		console.log(result);
	})

    document.querySelector('#post_text').value = "";

}

function edit_post(post_id) {

    var message = document.querySelector(`#message-${post_id}`).textContent
    document.querySelector(`#message-${post_id}`).innerHTML = ""

    const textarea = document.createElement("textarea")
    textarea.className = "form-control"
    textarea.innerHTML = message
    document.querySelector(`#message-${post_id}`).append(textarea)
    
    const pbreak = document.createElement("p")
    document.querySelector(`#message-${post_id}`).append(pbreak)

    const submit = document.createElement("button")
    submit.className = "btn btn-primary"
    submit.dataset.id = post_id
    submit.innerHTML = "Post"
    document.querySelector(`#message-${post_id}`).append(submit)

    document.querySelector(`#edit-${post_id}`).style.display = 'none'
    
    submit.onclick = () => {
        const message_content = textarea.value
        fetch(`editpost/${post_id}`, {
            method: 'PUT',
            body: JSON.stringify({
                message: message_content
            })
        })
        
        .then(response => response.json())
        .then(message => {
            const message_box = document.querySelector(`#message-${post_id}`)
            message_box.innerHTML = message
            
            document.querySelector(`#edit-${post_id}`).style.display = 'block'
        })
    }
}

function like(post_id, like_unlike) {

    fetch(`/like_unlike/${post_id}`, {

        method: 'PUT',
        body: JSON.stringify({
            like_unlike: like_unlike
        })
    })

    .then(response => response.json())
    .then(post => {

        document.querySelector(`#like-count-${post.id}`).innerHTML = post.like_count

        if (document.querySelector(`#like-btn-${post.id}`)) {
            document.querySelector(`#like-btn-${post.id}`).remove()
            var like_status = 'unlike'
            var src = 'static/network/like.svg'
            var id = `unlike-btn-${post_id}`

        } else if (document.querySelector(`#unlike-btn-${post.id}`)) {
            document.querySelector(`#unlike-btn-${post.id}`).remove()
            var like_status = 'like'
            var src = 'static/network/unlike.svg'
            var id = `like-btn-${post_id}`
        }

        const but = document.createElement('img')
        but.id = id
        but.className = 'btn-like'
        but.dataset.id = post_id
        but.dataset.like_status = like_status
        but.src = src

        but.onclick = () => {
            like(post_id, but.dataset.like_status)
        }

        document.querySelector(`#like-div-${post_id}`).append(but)
    })
    
}

function follow(profile_username, follow_unfollow) {
    fetch(`/follow/${profile_username}`, {

        method: 'PUT',
        body: JSON.stringify({
            follow_unfollow: follow_unfollow
        })
    })

    .then(response => response.json())
    .then(profile => {

        document.querySelector('#follow-count').innerHTML = `Followers: ${profile.followers_count}`

        if (document.querySelector('#follow-btn')) {
            document.querySelector('#follow-btn').remove()
            var follow_status = 'unfollow'
            var inner = 'Unfollow'
            var id = 'unfollow-btn'

        } else if (document.querySelector('#unfollow-btn')) {
            document.querySelector('#unfollow-btn').remove()
            var follow_status = 'follow'
            var inner = 'Follow'
            var id = 'follow-btn'
        }

        const but = document.createElement('button')
        but.id = id
        but.className = 'btn-follow'
        but.dataset.username = profile_username
        but.dataset.follow_status = follow_status
        but.innerHTML = inner

        but.onclick = () => {
            follow(profile_username, but.dataset.follow_status)
        }

        document.querySelector('.follow-btn-div').append(but)

    })
}