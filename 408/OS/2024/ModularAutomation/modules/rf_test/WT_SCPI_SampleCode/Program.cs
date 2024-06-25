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
        static readonly string all_freq = "2412,2417,2422,2427,2432,2437,2442,2447,2452,2457,2462,2467,2472,2484,5180,5190,5200,5210,5220,5230,5240,5250,5260,5270,5280,5290,5300,5310,5320,5500,5510,5520,5530,5540,5550,5560,5570,5580,5590,5600,5610,5620,5630,5640,5660,5670,5680,5690,5700,5710,5720,5745,5755,5765,5775,5785,5795,5805,5825,5835,5845,5855,5865,5875,5885,5935,5945,5955,5965,5975,5985,5995,6005,6015,6025,6035,6045,6055,6065,6075,6095,6105,6115,6125,6135,6145,6155,6165,6175,6185,6195,6205,6215,6235,6255,6265,6275,6285,6295,6305,6315,6325,6335,6345,6355,6365,6375,6385,6395,6415,6425,6435,6445,6455,6465,6475,6485,6495,6505,6515,6525,6535,6545,6555,6575,6585,6595,6605,6615,6625,6635,6645,6655,6665,6675,6685,6695,6705,6715,6735,6745,6755,6765,6775,6785,6795,6815,6835,6855,6875,6895,6915,6925,6935,6945,6955,6965,6975,6985,6995,7005,7015,7025,7035,7055,7065,7075,7095,7115,7125";

        static void Main(string[] args)
        {
            scpi = new WT_SCPI();
            Example_PAC();
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
            while (true)
            {
                HttpListenerContext context = listener.GetContext();
                string postData;
                using (var reader = new StreamReader(stream: context.Request.InputStream, encoding: context.Request.ContentEncoding))
                {
                    postData = reader.ReadToEnd();
                }
                byte[] responseBytes = Encoding.UTF8.GetBytes("Received.");
                context.Response.OutputStream.Write(buffer: responseBytes, offset: 0, count: responseBytes.Length);
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
                        Execute_task(jsonDict: jsonDict);
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
        static void Execute_task(JObject jsonDict)
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
                    case "PAC":
                        scpi.SetPACParam(
                            sense_port: int.Parse(jsonDict["VSA_PORT"].ToString()),
                            source_port: int.Parse(jsonDict["VSG_PORT"].ToString()),
                            sense_power_max: double.Parse(jsonDict["VSA_POWER_MAX"].ToString()),
                            source_power: double.Parse(jsonDict["VSG_POWER"].ToString()),
                            sense_sample: double.Parse(jsonDict["VSA_SAMPLE_TIME"].ToString()),
                            pac_mode: int.Parse(jsonDict["PAC_MODE"].ToString()),
                            pac_avg: int.Parse(jsonDict["PAC_AVG_COUNT"].ToString()),
                            pac_freq_list: jsonDict["PAC_FREQ_LIST"].ToString()
                            );
                        scpi.StartPAC();
                        Thread.Sleep(30000);
                        scpi.GetResultPAC();
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
        //static void Example_test()
        //{
        //    try
        //    {
        //        scpi.Connect("192.168.10.254");
        //        scpi.UploadWaveForm("./54 Mbps(OFDM)328.bwv");
        //        scpi.SetDevmParam(20, 200e-6, 500e-6);
        //        scpi.Vsg(5, 2412, 240, 0, "54 Mbps(OFDM)328.bwv", -10);
        //        Thread.Sleep(100);
        //        scpi.Vsa(6, 2412, 240, SignalDemod.Demod11ag);
        //        Console.WriteLine(scpi.GetResult());
        //    }
        //    catch (Exception ex)
        //    {
        //        Console.WriteLine(ex);
        //    }
        //    finally
        //    {
        //        scpi.Disconnect();
        //    }
        //}
        static void Example_PAC()
        {
            scpi.Connect("192.168.10.254");
            scpi.SetPACParam(
            sense_port: 1,
            source_port: 2,
            sense_power_max: -10.0,
            source_power: -10.0,
            sense_sample: 0.002,
            pac_mode: 0,
            pac_avg: 10,
            pac_freq_list: all_freq
            );
            scpi.StartPAC();
            Thread.Sleep(30000);
            scpi.GetResultPAC();
        }
    }
}
