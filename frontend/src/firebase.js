import Firebase from 'firebase'

require('firebase/firestore')

const firebaseApp = Firebase.initializeApp({
    apiKey: "AIzaSyAr2nAjQPlikZhfkrzPqjfM0d5JtxYIORU",
    authDomain: "servian-chris-sandbox.firebaseapp.com",
    databaseURL: "https://servian-chris-sandbox.firebaseio.com",
    projectId: "servian-chris-sandbox",
    storageBucket: "servian-chris-sandbox.appspot.com",
    messagingSenderId: "425411032467"
})

export const db = firebaseApp.firestore()