using System;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;
using Newtonsoft.Json.Linq;

namespace WT_SCPI_SampleCode
{
    class Program
    {
        static void Main(string[] args)
        {
            HttpListener listener = new HttpListener();
            listener.Prefixes.Add("http://localhost:20291/");
            listener.Start();
            while (true) {
                HttpListenerContext context = listener.GetContext();
                string postData;
                using (var reader = new StreamReader(stream: context.Request.InputStream, encoding: context.Request.ContentEncoding)) { 
                    postData = reader.ReadToEnd();
                }
                byte[] responseBytes = Encoding.UTF8.GetBytes("Received.");
                context.Response.OutputStream.Write(buffer:responseBytes,offset:0,count:responseBytes.Length);
                context.Response.Close();
                try
                {
                    JObject jsonDict = JObject.Parse(postData);
                    Console.WriteLine("Received JSON data:");
                    foreach (var pair in jsonDict)
                    {
                        Console.WriteLine($"{pair.Key}: {pair.Value}");
                    }
                }
                catch (Exception)
                {
                    // 如果解析失败，直接输出原始数据
                    Console.WriteLine("Received TEXT data:");
                    Console.WriteLine(postData);
                }
            }
        }
        void execute_test() {
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
