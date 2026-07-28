package com.attendsense.ui

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.NavController
import androidx.navigation.fragment.NavHostFragment
import com.attendsense.R
import com.attendsense.utils.SessionManager

/**
 * MainActivity — the single activity that hosts the entire app.
 *
 * Navigation Component manages all screen transitions.
 * On launch:
 *   → Already logged in  : skip Login, go straight to Home
 *   → Not logged in      : show Login screen
 */
class MainActivity : AppCompatActivity() {

    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        navController = navHostFragment.navController

        // Skip login if session token already exists
        val session = SessionManager(this)
        if (session.isLoggedIn()) {
            navController.navigate(R.id.action_login_to_home)
        }
    }
}