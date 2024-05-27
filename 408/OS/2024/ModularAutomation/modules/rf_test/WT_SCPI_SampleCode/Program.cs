using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;

namespace WT_SCPI_SampleCode
{
    class Program
    {
        static void Main(string[] args)
        {
            WT_SCPI scpi = new WT_SCPI();
            try
            {
                scpi.Connect("192.168.10.254");
                scpi.UploadWaveForm("./54 Mbps(OFDM)328.bwv");

                scpi.SetDevmParam(20, 200e-6, 500e-6);
                scpi.Vsg(5, 2412, 240, 0, "54 Mbps(OFDM)328.bwv");
                Thread.Sleep(100);
                scpi.Vsa(6, 2412, 240, SignalDemod.Demod11ag);
                Console.WriteLine(scpi.GetResult());
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex);
            }
            finally
            {
                scpi.Disconnect();
            }
        }
    }
}
