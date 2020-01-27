package com.snopf.snopf

import android.app.Dialog
import android.content.Context
import android.content.DialogInterface
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.view.Menu
import android.view.MenuInflater
import android.view.MenuItem
import android.view.View
import android.widget.NumberPicker
import androidx.appcompat.app.AlertDialog
import kotlinx.android.synthetic.main.activity_main.*
import kotlinx.android.synthetic.main.settings_dialog.*

class MainActivity : AppCompatActivity() {

    private val usbVendorRequest = 0x40

    private var passwordLength = MAX_PASSWORD_LENGTH
    private var passwordIteration = 0
    private var autoHitEnter = false

    fun resetPasswordSettings() {
        passwordLength = MAX_PASSWORD_LENGTH
        passwordIteration = 0
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }

    fun onClickOk(button: View) {
        val pin = editPin.text.toString()
        val hostname = hostnameSelect.text.toString()
        val account = accountSelect.text.toString()

        val pwRequest = passwordRequest(hostname, account, pin, 0)

        val snopfDevice = intent.getParcelableExtra(UsbManager.EXTRA_DEVICE) as UsbDevice?
        val usbManager = getSystemService(Context.USB_SERVICE) as UsbManager
        val conn = usbManager.openDevice(snopfDevice)

        if (conn == null) {
            showInfo("Missing USB device", "USB device not found.")
            return
        }

        val rawRequest = usbRequest(pwRequest, passwordLength, autoHitEnter)

        // If the device is found we just send the request and close this activity because
        // we would just be in the way any ways
        // TODO save new information before closing if necessary
        conn.controlTransfer(usbVendorRequest, 0, 0, 0,
            rawRequest, rawRequest.size, 0)

        this.finish()
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        val inflater: MenuInflater = menuInflater
        inflater.inflate(R.menu.settings_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Handle item selection
        return when (item.itemId) {
            R.id.password_settings -> {
                val alertDialog: AlertDialog? = this.let {
                    val builder = AlertDialog.Builder(it)
                    val inflater = layoutInflater
                    inflater?.let {
                        builder.setView(inflater.inflate(R.layout.settings_dialog, null))
                            .setPositiveButton(R.string.ok,
                                DialogInterface.OnClickListener { dialogInterface, id ->
                                    var dialog = dialogInterface as Dialog
                                    passwordLength = dialog.findViewById<NumberPicker>(
                                        R.id.passwordLengthPicker).value
                                    passwordIteration = dialog.findViewById<NumberPicker>(
                                        R.id.passwordIterationPicker).value
                                })
                            .setNegativeButton(R.string.cancel,
                                DialogInterface.OnClickListener { dialog, id ->
                                    // Just ignore it
                                })
                    }
                    builder.create()
                }
                alertDialog?.let {
                    it.show()
                    it.passwordLengthPicker.maxValue = MAX_PASSWORD_LENGTH
                    it.passwordLengthPicker.minValue = MIN_PASSWORD_LENGTH
                    it.passwordLengthPicker.value = passwordLength
                    it.passwordLengthPicker.wrapSelectorWheel = false
                    it.passwordIterationPicker.minValue = 0
                    it.passwordIterationPicker.maxValue = 999
                    it.passwordIterationPicker.value = passwordIteration
                    it.passwordIterationPicker.wrapSelectorWheel = false
                }
                true
            }
            R.id.info -> {
                showInfo("Version", "Commit: " + BuildConfig.GitHash)
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
    
    fun showInfo(title: String, message: String) {
        val alertDialog = AlertDialog.Builder(this).create()
        alertDialog.setTitle(title)
        alertDialog.setMessage(message)
        alertDialog.setButton(AlertDialog.BUTTON_NEUTRAL, "OK") {
                dialog, which -> dialog.dismiss() }
        alertDialog.show()
    }
}
