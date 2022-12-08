'use strict';

document.addEventListener('DOMContentLoaded', () => {

    let followButton = document.querySelector('#follow-state-button');
    let personId = Number(document.querySelector('#creator-id').innerHTML);
    // Add an event to Follow or Unfollow a person
    followButton.addEventListener('click', function () {setFollowState(personId, followButton)});
});

function setFollowState(personId, button) {
    // Based on the inner html from the button, put its opposit to the server
    let buttonContent = button.innerHTML == "Follow" ? "Unfollow" : "Follow";
    fetch(`/alter_follow_state/${personId}`, {
        "method": 'PUT',
        body: JSON.stringify({
            state: buttonContent,
        })
    })
    .catch(error => console.log(error));

    button.innerHTML = buttonContent;
};