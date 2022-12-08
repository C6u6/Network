'use strict';

document.addEventListener('DOMContentLoaded', () => {
    // Add an event that will allow user to like or unlike a post
    document.querySelectorAll('.like-button').forEach( element => {
        let postIdInButton = element.getAttribute('id');
        element.addEventListener('click', function () {likeOrUnlike(postIdInButton, element)});
    });

    // Add an event to edit buttons
    document.querySelectorAll('.edit-content-post').forEach( button => {
        let postIdInButton = button.getAttribute('id');
        button.addEventListener('click', function () {editContent(postIdInButton)});
    });

    // Show the edited time post, if any
    showEditedTime();
});

function likeOrUnlike(postId, button) {
    // Make a PUT request to update the number of likes in a post
    fetch(`update_likes/${postId}`, {
        method: "POST",
        body: JSON.stringify({
            ilustrativeKey: '',
        }) 
    })
    .catch(error => console.log(error));
}


function editContent(postId) {

    // Make a form to insert in place of the post content
    let form = document.createElement('form');
    form.setAttribute('action', "{% url 'edit' %}");
    form.setAttribute('method', 'PUT');

    let submitButton = document.createElement('input')
    submitButton.value =  'Save';
    submitButton.type = 'button';
    submitButton.disabled = true;

    let textarea = document.createElement('textarea');
    textarea.setAttribute('placeholder', 'Edit this post');
    textarea.setAttribute('name', 'new-content');

    let closeButton = document.createElement('button');
    closeButton.innerHTML = '&times';

    // Able the submitButton if the textarea has at least a char
    textarea.addEventListener('input', function (e) {

        if (e.target.value.length == 0) {
            submitButton.disabled = true;
        }
        else {
            submitButton.disabled = false;
        }
    });

    // Compose the form
    form.append(textarea, submitButton, closeButton);

    // In the div, substitute the post conten by a form, storing the old content before that
    let content = document.querySelector(`#content-post-id-${postId}`).innerHTML;
    document.querySelector(`#content-post-id-${postId}`).innerHTML = '';
    document.querySelector(`#content-post-id-${postId}`).append(form);

    // If user clicks the closeButton, reload the old content
    closeButton.addEventListener('click', () => {
        document.querySelector(`#content-post-id-${postId}`).innerHTML = content;
    });

    // Send the new info to the appropriete route
    submitButton.addEventListener('click', () => {
        if (!submitButton.disabled) {
            // Send through fetch
            fetch(`/edit/${postId}`, {
                'method': 'PUT',
                body: JSON.stringify({
                    content: textarea.value,
                })
            })
            .catch(error => console.log(error));

            // Substitute the form by the new post content
            document.querySelector(`#content-post-id-${postId}`).innerHTML = textarea.value; 

            // Show the time that the post was changed
            showEditedTime();
        }
    })
}

function showEditedTime() {
    let created_at = document.querySelector('#created_at');
    let updated_at = document.querySelector('#updated_at');

    if (created_at.innerHTML != updated_at.innerHTML) {
        updated_at.hidden = false;
    };
}