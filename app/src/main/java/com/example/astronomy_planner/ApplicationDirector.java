package com.example.astronomy_planner;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import java.io.IOException;
import android.util.Log;


public class ApplicationDirector extends AppCompatActivity
{
    @Override protected void onCreate(Bundle savedInstance)
    {
        super.onCreate(savedInstance);

        //setup default cases
        int lat = 0;
        int lon = 0;

        String[] astroDataLoad =  {
                "python",
                "/AstroDataLoader.py",
                Integer.toString(lat),
                Integer.toString(lon)
        };

        Log.d("AstroDBG", "Program has successfully started");
    }

}
