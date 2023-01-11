window.addEventListener('load', () => {

const starListEl = document.querySelector('.star-list');
const starCountInput = document.querySelector('#star-count');

let starOrderState = 0;

const stars = starListEl.children

function makeStared(el) {
    el.className = 'fas fa-star'
}

function makeUnstared(el) {
    el.className = 'far fa-star'
}

function stared(order) {
    for (let star of stars) {
        const starOrder = +star.getAttribute('data-order');
        if (starOrder <= order) {
            makeStared(star)
        } else {
            makeUnstared(star)
        }
    }
}


for (let star of stars) {
    star.onmouseenter = (e) => {
        const starOrder = e.target.getAttribute('data-order');
        stared(starOrder);
    }

    star.onclick = (e) => {
        const starOrder = e.target.getAttribute('data-order');
        starOrderState = starOrder;
        stared(starOrder);
        starCountInput.value = starOrder
    }
}

starListEl.onmouseleave = (e) => {
    stared(starOrderState)
}




})