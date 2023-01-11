window.addEventListener('load', () => {
let state = window.location.search.slice(1,).split('&').map(e => e.split('='))

const filterButton = document.querySelector('.filter-button')

const colors = state.filter(color => color[0] === 'color')
const allColorInput = document.querySelector('#color-all')
const colorInputs = document.querySelectorAll('.color-input')
if (colors.length) {
    colors.forEach(color => {
        const colorInput = document.querySelector('#color-'+color[1]);
        colorInput.checked = true;
    })
} else {
    allColorInput.checked = true;
}
allColorInput.addEventListener('change', (e) => {
    if (e.target.checked) {
        colorInputs.forEach(i => i.checked=false);
        state = state.filter(el => el[0] !== 'color')
    } else {
        e.target.checked = true;
    }
})

colorInputs.forEach(i => {
    i.addEventListener('change', (e) => {
        allColorInput.checked = false;
        const checked = e.target.checked
        const title = e.target.getAttribute('data-title')
        if (checked) {
            allColorInput.checked = false;
            state.push(['color', title])
        } else {
            state = state.filter(e => !(e[0] === 'color' && e[1] === title))

            if (!state.find(e => e[0] === 'color')) {
                allColorInput.checked = true;
            }
        }
    })
})





const sizes = state.filter(size => size[0] === 'size')
const allSizeInput = document.querySelector('#size-all')
const sizeInputs = document.querySelectorAll('.size-input')
if (sizes.length) {
    sizes.forEach(size => {
        const sizeInput = document.querySelector('#size-'+size[1]);
        sizeInput.checked = true;
    })
} else {
    allSizeInput.checked = true;
}
allSizeInput.addEventListener('change', (e) => {
    if (e.target.checked) {
        sizeInputs.forEach(i => i.checked=false);
        state = state.filter(el => el[0] !== 'size')
    } else {
        e.target.checked = true;
    }
})

sizeInputs.forEach(i => {
    i.addEventListener('change', (e) => {
        allSizeInput.checked = false;
        const checked = e.target.checked
        const title = e.target.getAttribute('data-title')
        if (checked) {
            allSizeInput.checked = false;
            state.push(['size', title])
        } else {
            state = state.filter(e => !(e[0] === 'size' && e[1] === title))

            if (!state.find(e => e[0] === 'size')) {
                allSizeInput.checked = true;
            }
        }
    })
})

let priceError = false;
const minPriceEl = document.querySelector('#min-price')
const maxPriceEl = document.querySelector('#max-price')
minPriceEl.value = state.find(arr => arr[0]==='min_price')?.[1] || ''
maxPriceEl.value = state.find(arr => arr[0]==='max_price')?.[1] || ''
const minLimit = Number(minPriceEl.getAttribute('limitvalue'))
const maxLimit = Number(maxPriceEl.getAttribute('limitvalue'))

minPriceEl.oninput = (e) => {
    const value = Number(e.target.value);
    const maxValue = Number(maxPriceEl.value) || maxLimit
    if (value > minLimit && value < maxValue) {
        minPriceEl.style.borderColor = '#ced4da'
        priceError = false;
        filterButton.style.opacity = '1'
    } else {
        minPriceEl.style.borderColor = 'red'
        priceError = true;
        filterButton.style.opacity = '0.3'
    }
}

maxPriceEl.oninput = (e) => {
    const value = Number(e.target.value);
    const minValue = Number(minPriceEl.value) || minLimit
    if (value < maxLimit && value > minValue) {
        maxPriceEl.style.borderColor = '#ced4da'
        priceError = false;
        filterButton.style.opacity = '1'
    } else {
        maxPriceEl.style.borderColor = 'red'
        priceError = true;
        filterButton.style.opacity = '0.3'
    }
}


filterButton.onclick = () => {
    state = state.filter(arr => !arr[0].endsWith('price'))
    const page = state.find(arr => arr[0]==='page')
    if (page) page[1] = 1
    minPriceEl.value && state.push(['min_price', minPriceEl.value])
    maxPriceEl.value && state.push(['max_price', maxPriceEl.value])
    console.log(state)
    const querystring = state.map(arr => arr.join('=')).join('&')
    window.location.search = '?' + querystring    
}
















})