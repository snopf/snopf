package com.snopf.snopf

import java.security.MessageDigest

val MSG_LENGTH = 16
val MIN_PASSWORD_LENGTH = 6
val MAX_PASSWORD_LENGTH = 40

// Hashes the given byte message (UTF-8 encoded concatenated password request)
// and reduces the length to the message length for snopf
fun reduceMessage(byteMessage: ByteArray): ByteArray {
    val sha256 = MessageDigest.getInstance("SHA-256")
    val hash = sha256.digest(byteMessage)
    // Kotlin is weird and includes the upper limit, thus MSG_LENGTH -1
    return hash.slice(0..MSG_LENGTH - 1).toByteArray()
}

// Get a password request byte message to send to the device from
// the given parameters
fun passwordRequest(hostname: String, account: String, pin: String,
                    passwordIteration: Int) : ByteArray {
    // The password iteration is defined to be empty if it's zero, else it is
    // str(number)
    var strPasswordIteration = passwordIteration.toString()
    if (passwordIteration == 0) {
        strPasswordIteration = ""
    }
    // The important part is the order of concatenation, this must be the same
    // on all implementations / request building software
    val concatMessage = (hostname + account + pin + strPasswordIteration)
    return reduceMessage(concatMessage.toByteArray(Charsets.UTF_8))
}

fun usbRequest(requestMessage: ByteArray, passwordLength: Int,
               hitEnter: Boolean = false) : ByteArray {
    var ctrlByte = ByteArray(1) {(0).toByte()}
    if (hitEnter) {
        ctrlByte[0] = (1).toByte()
    }
    return ctrlByte + ByteArray(1){passwordLength.toByte()} + requestMessage
}