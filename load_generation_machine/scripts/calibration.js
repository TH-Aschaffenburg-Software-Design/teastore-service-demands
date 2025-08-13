import { Request, Client } from "k6/x/fasthttp"
import file from 'k6/x/file'
import execution from 'k6/execution'
import { SharedArray } from 'k6/data';

const requestsFile = "./generated/requests.json"
const requestData = JSON.parse(file.readFile(requestsFile))[__ENV.REQUEST]

export const options = {
    scenarios: {
        [requestData.name]: {
            executor: 'constant-arrival-rate',
            rate: requestData.rate,
            timeUnit: '1s',
            duration: '125s', // 100s real timeframe, 20s warmup before and 5s buffer after
            preAllocatedVUs: Math.floor(requestData.rate / 2),
            maxVUs: requestData.rate * 2
        },
    },
    discardResponseBodies: true, // faster
}

const productsArray = new SharedArray('products', function () {
    const productsFile = "./generated/products.json"
    const arr = JSON.parse(file.readFile(productsFile))
    return arr;
});

const sessionBlobs = new SharedArray('sessionBlobs', function () {
    const sessionBlobsFile = "./generated/sessionBlobs.json"
    const arr = JSON.parse(file.readFile(sessionBlobsFile))
    return arr;
});

const queryParams = {
    "{category_id}": () => getIntBetween(2, 6),
    "{product_id}": getProductId,
    "{product_id_not_in_cart}": getProductIdNotInCart,
    "{product_id_in_cart}": () => { return sessionBlobs[getIntBetween(0, 99)].orderItems[0].productId },
    "{user_id}": () => { return sessionBlobs[getIntBetween(0, 99)].uid },
    "{user_num}": () => { return getIntBetween(0, 99) },
    "{page}": () => getIntBetween(1, 5),
    "{start}": () => getIntBetween(0, 49),
    "{max}": () => getIntBetween(1, 50),
    "{quantity}": () => getIntBetween(1, 10),
    "{order_details}": getOrderDetails
}

const bodyParams = {
    "blob": () => { return sessionBlobs[getIntBetween(0, 99)] },
    "order": getOrder,
    "orderItem": () => { return sessionBlobs[getIntBetween(0, 99)].orderItems[0] },
    "orderItemArray": () => { return sessionBlobs[getIntBetween(0, 99)].orderItems },
    "productImages": getProductImages,
    "webImages": () => { return { "icon": "64x64" } } // only web image that exists
}

const header = { 'Content-Type': 'application/json' }
const imageArray = [
    ["64x64", () => { return [5, 10, 20, 30, 50][getIntBetween(0, 4)] }],
    ["125x125", () => 3],
    ["300x300", () => 1]
]

const client = new Client()

let iteration = 0

export function setup() {

    return requestData
}

export default function (data) {

    let path = data.path
    Object.entries(queryParams).forEach(([placeholder, generate]) => {
        if (path.includes(placeholder)) {
            path = path.split(placeholder).join(generate());
        }
    });

    const fullUrl = data.endpoint + path

    let body = null
    if (data.body) {
        if (bodyParams.hasOwnProperty(data.body)) {
            body = JSON.stringify(bodyParams[data.body]())
        } else {
            body = JSON.stringify(data.body)
        }
    }

    const request = new Request(fullUrl)

    switch (data.method) {
        case "GET":
            client.get(request)
            break
        case "POST":
            client.post(request, { body: body, headers: header })
            break
        case "PUT":
            client.put(request, { body: body, headers: header })
            break
    }
    iteration = execution.scenario.iterationInInstance
}

// Min and max both inclusive
function getIntBetween(min, max) {
    const range = max - min + 1;
    return min + (iteration % range);
}

function getProductId(offset = 0) {
    let index = getIntBetween(0, productsArray.length - 1)
    index = (index + offset) % productsArray.length
    return productsArray[index].id
}

function getProductIdNotInCart() {
    for (let i = 0; ; i++) {
        const productId = getProductId(i)
        let id = (productId + 1) % productsArray.length
        if (sessionBlobs[getIntBetween(0, 99)].orderItems.find(e => e.productId === id) === undefined) {
            return id
        }
    }
}

function getOrder() {

    return ({
        userId: sessionBlobs[getIntBetween(0, 99)].uid,
        totalPriceInCents: 999,
        addressName: "First Last",
        address1: "Address1",
        address2: "Address2",
        creditCardCompany: "Company",
        creditCardNumber: "1111 2222 3333 4444",
        creditCardExpiryDate: "2050-01-01"
    })
}

function getProductImages() {

    const image = imageArray[getIntBetween(0, 2)]
    const size = image[0]
    const amount = image[1]()
    const startId = getIntBetween(0, productsArray.length - 1 - amount)
    let images = {}
    for (let i = startId; i < amount; i++) {
        images[productsArray[i].id] = size
    }
    return images
}

function getQueryParams(obj) {

    return Object.keys(obj).reduce(
        (a, k) => {
            a.push(k + '=' + encodeURIComponent(obj[k]))
            return a
        }, []
    ).join('&')
}

function getOrderDetails() {
    const full_order = getOrder()
    const { userId, ...order } = full_order
    const params = getQueryParams(order)
    return params
}
