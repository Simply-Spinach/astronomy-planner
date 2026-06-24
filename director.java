import java.io.IOException;
import android.location.Location;
import android.location.LocationManager;


public class director
{
    public static void main()
    {
        try
        {
            int lat;
            int lon;

            String[] astroDataLoad =  {
                    "python",
                    "./AstroDataLoader.py",
                    lat.toString(),
                    lon.toString()
            };
        }
        catch (IOException e)
        {
            System.out.println("Error: Python failed to run");
        }
    }

}
