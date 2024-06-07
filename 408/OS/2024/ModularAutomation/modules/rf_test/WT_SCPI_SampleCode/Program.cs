using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;
using Newtonsoft.Json.Linq;

namespace WT_SCPI_SampleCode
{
    class Program
    {
        static WT_SCPI scpi;
        static Dictionary<String, SignalDemod> demod_dict;



        static void Main(string[] args)
        {
            scpi = new WT_SCPI();
            demod_dict = new Dictionary<string, SignalDemod>();
            demod_dict.Add(key: "Demod11ag", value: SignalDemod.Demod11ag);
            demod_dict.Add(key: "Demod11b", value: SignalDemod.Demod11b);
            demod_dict.Add(key: "Demod11n20", value: SignalDemod.Demod11n20);
            demod_dict.Add(key: "Demod11n40", value: SignalDemod.Demod11n40);
            demod_dict.Add(key: "Demod11ac20", value: SignalDemod.Demod11ac20);
            demod_dict.Add(key: "Demod11ac40", value: SignalDemod.Demod11ac40);
            demod_dict.Add(key: "Demod11ac80", value: SignalDemod.Demod11ac80);
            demod_dict.Add(key: "Demod11ac160", value: SignalDemod.Demod11ac160);
            demod_dict.Add(key: "Demod11ac8080", value: SignalDemod.Demod11ac8080);
            demod_dict.Add(key: "DemodBluetooth", value: SignalDemod.DemodBluetooth);
            demod_dict.Add(key: "DemodZigbee", value: SignalDemod.DemodZigbee);
            demod_dict.Add(key: "DemodCW", value: SignalDemod.DemodCW);
            demod_dict.Add(key: "Demod11ax20", value: SignalDemod.Demod11ax20);
            demod_dict.Add(key: "Demod11ax40", value: SignalDemod.Demod11ax40);
            demod_dict.Add(key: "Demod11ax80", value: SignalDemod.Demod11ax80);
            demod_dict.Add(key: "Demod11ax160", value: SignalDemod.Demod11ax160);
            demod_dict.Add(key: "Demod11ax8080", value: SignalDemod.Demod11ax8080);
            demod_dict.Add(key: "Demod11be20", value: SignalDemod.Demod11be20);
            demod_dict.Add(key: "Demod11be40", value: SignalDemod.Demod11be40);
            demod_dict.Add(key: "Demod11be80", value: SignalDemod.Demod11be80);
            demod_dict.Add(key: "Demod11be160", value: SignalDemod.Demod11be160);
            demod_dict.Add(key: "Demod11be8080", value: SignalDemod.Demod11be8080);
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
                    if (jsonDict.ContainsKey("TASK"))
                    {
                        execute_task(jsonDict: jsonDict);
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
        static void execute_task(JObject jsonDict)
        {
            try
            {
                string task = jsonDict["TASK"].ToString();
                switch (task)
                {
                    case "CONNECT":
                        scpi.Connect(jsonDict["HOST"].ToString());
                        break;
                    case "UPLOAD":
                        scpi.UploadWaveForm(jsonDict["BWV"].ToString());
                        break;
                    case "SET_DEVM":
                        scpi.SetDevmParam(
                            dutyRadio: int.Parse(jsonDict["DEVM_DUTY_RADIO"].ToString()),
                            leadTime: double.Parse(jsonDict["DEVM_LEAD_TIME"].ToString()), 
                            delayTime: double.Parse(jsonDict["DEVM_DELAY_TIME"].ToString())
                            );
                        break;
                    case "VSG":
                        scpi.Vsg(
                            port: int.Parse(jsonDict["VSG_PORT"].ToString()),
                            freqMHz: int.Parse(jsonDict["VSG_FREQ_MHZ"].ToString()),
                            sampleRateMHz: int.Parse(jsonDict["VSG_SAMPLE_RATE_MHZ"].ToString()),
                            packets: int.Parse(jsonDict["VSG_PACKETS"].ToString()),
                            wave: jsonDict["VSG_WAVE"].ToString(),
                            pow: int.Parse(jsonDict["VSG_POW"].ToString())
                            );
                        break;
                    case "VSA":
                        scpi.Vsa(
                            port: int.Parse(jsonDict["VSA_PORT"].ToString()),
                            freqMHz: int.Parse(jsonDict["VSA_FREQ_MHZ"].ToString()),
                            sampleRateMHz: int.Parse(jsonDict["VSA_SAMPLE_RATE_MHZ"].ToString()),
                            demod: demod_dict[jsonDict["VSA_DEMOD"].ToString()]
                            );
                        break;
                    case "RESULT":
                        string res = scpi.GetResult();
                        File.WriteAllText(jsonDict["RESULT_TXT"].ToString(), res);
                        break;
                }
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
        static void example_test() {
            try
            {
                scpi.Connect("192.168.10.254");
                scpi.UploadWaveForm("./54 Mbps(OFDM)328.bwv");

                scpi.SetDevmParam(20, 200e-6, 500e-6);
                scpi.Vsg(5, 2412, 240, 0, "54 Mbps(OFDM)328.bwv",-10);
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
