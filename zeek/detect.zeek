@load base/protocols/dnp3
@load base/frameworks/sumstats
@load base/utils/time

global number = -1;
global time_seq:vector of time;

module DNP3;

export {
    redef enum Notice::Type +={
        FrequentAccessWarning
    };
    const threshold: double = 3 ;
    const time_interval =  3 secs ;
    
}
event dnp3_application_request_header(c: connection, is_orig: bool, application_control: count, fc: count)
	{
	number = number+1;
    if ( ! c?$dnp3 )
		c$dnp3 = [$ts=network_time(), $uid=c$uid, $id=c$id];
#    print c;
    time_seq += network_time();
    print fmt("The connection %s from %s on port %s to %s on port %s started at %s.", c$uid, c$id$orig_h, c$id$orig_p, c$id$resp_h, c$id$resp_p, network_time()-time_seq[0]); 
    if(number>0 && time_seq[number] - time_seq[number-1] > time_interval){
        print "";
        print "##################################################";
        print fmt("Delay attack warning from ip: %s", c$id$orig_h);
        print "##################################################";
        print "";
    }
	c$dnp3$ts = network_time();
	c$dnp3$fc_request = function_codes[fc];
    #print cat(c$id$resp_h);
    SumStats::observe("dnp.connect", [$host=c$id$orig_h], [$str=cat(c$id$resp_h)]);
	}

event zeek_init()
    {
    local r1: SumStats::Reducer = [$stream="dnp.connect", $apply=set(SumStats::UNIQUE), $unique_max=double_to_count(threshold+2)];
    SumStats::create([$name="dnp_connection",
                      $epoch=time_interval,
                      $reducers=set(r1),
                      $threshold_val(key: SumStats::Key, result: SumStats::Result) =
                          {
                          return result["dnp.connect"]$num+0.0;
                          },
                      $threshold=threshold,
                      $threshold_crossed(key: SumStats::Key, result: SumStats::Result) =
                          {
                          local r = result["dnp.connect"];
                          local dur = duration_to_mins_secs(r$end-r$begin);
                          local plural = r$unique>1 ? "s" : "";
                          #print key;
                          local message = fmt("%s had %d connections  on server%s in %s", key$host, r$num,  plural, dur);
                          NOTICE([$note=DNP3::FrequentAccessWarning,
                                  $src=key$host,
                                  $msg=message,
                                  $identifier=cat(key$host)]);
                          }]);
    }





