package com.snopf.snopf

import android.util.Log
import org.json.JSONObject
import org.junit.Test
import org.junit.Assert.*
import java.io.File
import java.util.*

class RequestsTest {

    fun testEntry(entry:JSONObject) {
        var hostname = entry.getString("hostname")
        var account = entry.getString("account")
        var pin = entry.getString("pin")
        var password_iteration = entry.getInt("password_iteration")

        var request = passwordRequest(hostname, account, pin, password_iteration)

        // The Base64 decoder doesn't accept newline at end of string
        var rawExpectedRequest = entry.getString("request").removeSuffix("\n")
        var expectedRequest = Base64.getDecoder().decode(rawExpectedRequest)

        assertArrayEquals(request, expectedRequest)
    }

    @Test
    fun passwordRequestsTest() {
        var testFile = javaClass.classLoader?.getResource("test_vectors_password_creation.json")
        var testData = JSONObject(testFile?.readText(Charsets.UTF_8)).getJSONArray("tests")

        for(i in 0 until testData.length()) {
            var entry = testData.getJSONObject(i)
            testEntry(entry)
        }
    }
}