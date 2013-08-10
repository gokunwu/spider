#!/usr/bin/perl -w
use warnings;
use strict;
use DBI;
use Encode;
use Encode qw(from_to);
use URI::Escape qw(uri_escape);

@ARGV==1 or die("please input the config file!\n");
die("the config file :$ARGV[0] does not exists!\n ")unless(-e $ARGV[0]);

print "the spider: chemnet_spider starts at:";
system "date";

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
$year+=1900;
$mon+=1;
$mon="0".$mon if($mon<10);
$mday="0".$mday if($mday<10);
#my $today="$year-$mon-$mday";
#my $local_time="$mon-$mday";
my $today="2012-04-06";
my $local_time="04-06";
print "$today\n$local_time\n";

use constant SITE_ID=>6;
my $site_urll="http://news.chemnet.com";
my $ua_header="\"User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3\"";

my %baseurl_hash;
my ($file_path,$dbname,$tbname,$dbuser,$dbpwd,$save)=&ReadConfig($ARGV[0],\%baseurl_hash);
#print "$file_path\t$dbname\t$tbname\t$dbuser\t$dbpwd\t$save\n";
system "mkdir -p $file_path";
my $filepath_urllog=$file_path."/urllog";
system "mkdir -p $filepath_urllog";
my $filepath_basepage=$file_path."/basepage";
system "mkdir -p $filepath_basepage";
my $filepath_subpage=$file_path."/subpage";
system "mkdir -p $filepath_subpage";

my $dbh=DBI->connect("DBI:mysql:host=127.0.0.1;database=$dbname",$dbuser,$dbpwd,{'RaiseError'=>1});
$dbh->do("set names 'utf8'");
my $sql="insert ignore into $tbname(siteid,title,url,src,updatetime,channel,content,size,mainbody_flag,mainbody,mainbody_cut_flag,mainbody_cut)values(?,?,?,?,?,?,?,?,?,?,?,?)";
my $sth=$dbh->prepare($sql);

foreach my $channel (keys %baseurl_hash)
{
	print "$baseurl_hash{$channel}{0}\t$channel\t$baseurl_hash{$channel}{1}\n";
	my %suburl_hash;
	my $filename_urllog=$filepath_urllog."/downloadedurl_chemnet_".$today.".txt";
	&GetSubUrl($today,$filepath_basepage,$channel,$baseurl_hash{$channel}{1},\%suburl_hash);
	&DeleteDownloadedUrl($filename_urllog,\%suburl_hash);

	&DownWebpages($today,$filepath_subpage,$channel,$baseurl_hash{$channel}{0},\%suburl_hash);
	&RecordDownloadedUrl($filename_urllog,\%suburl_hash);
}

print "the spider:spider_chemnet finished at";
system "date";
print "**************************************************************************************\n\n\n";

sub RecordDownloadedUrl
{
	my ($filename_subpage,$suburl_hash)=@_;
	if(open(FW,">>$filename_subpage"))
	{
		foreach my $suburl (keys %$suburl_hash)
		{
			print FW "$suburl\n";
		}
		close(FW);
	}
	else
	{
		print "could not open the file :$filename_subpage to read!\n";
	}
}

sub DownWebpages
{
	my($today,$filepath_subpage,$channel_en,$channel_cn,$suburl_hash)=@_;
	my($title,$author,$src,$updatetime,$content,$size,$mainbody_flag,$mainbody,$mainbody_cut_flag,$mainbody_cut);
	$filepath_subpage=$filepath_subpage."/".$channel_en;
	system "mkdir -p $filepath_subpage";
	my $num=1;

	foreach my $suburl (keys %$suburl_hash)
	{
		my $filename_subpage=$filepath_subpage."/subpage_".$today."_".$num++.".html";
		unless(-e $filename_subpage)
		{
			`wget \"$suburl\" -O \"$filename_subpage\" -t 1 --timeout=30 --header=$ua_header`;
		}
		$size=-s $filename_subpage;
		if(1000>$size)
		{
			`wget \"$suburl\" -O \"$filename_subpage\" -t 1 --timeout=30 --header=$ua_header`;
			$size=-s $filename_subpage;
		}
		if((1000>$size)&&(1_000_000<$size))
		{
			unlink($filename_subpage);
			next;
		}
		if(open(FR,"$filename_subpage"))
		{
			print "dealing with the subpage file:$filename_subpage...\n";
			my $str;
			while(<FR>)
			{
				$str.=$_;
			}
			close(FR);
			#$str =~ s/&nbsp;/\x20/g;
			from_to($str,"gb2312","utf8");
			if($str=~m/<H1>(.*?)<\/H1>/is)
			{
				print "title:$1\n";
				$title=$1;
			}
			if($str=~m/<span class="red12px">\s*(.*?)\s*<\/span>/is)
			{
				$src=$1;
				$src=~s/\s+$//;
				$src=~s/<\/a>$//isg;
				$src=~s/^<a href="http:\/\/www\.chemnet\.com\.cn">//isg;
				print "src:$src\n";
			}
			if($str=~m/<td class="black14" id="maintext" style="line-height:180%; color:#000000; padding-top:10px;" >\s*(.*?)\s*<\/td>/is)
			{
				$mainbody_cut=$1;
				$mainbody=$mainbody_cut;
				&CleanMainbody(\$mainbody);
				#print "$mainbody\n";
			}
			$mainbody_flag=1 if((defined $mainbody)&&(0!=length $mainbody));
			$mainbody_cut_flag=1 if((defined $mainbody_cut)&&(0!=length $mainbody_cut));
			$sth->execute(SITE_ID,$title,$suburl,$src,$today,$channel_cn,$str,$size,$mainbody_flag,$mainbody,$mainbody_cut_flag,$mainbody_cut);
		}
		else
		{	print "could not open the file:$filename_subpage";}
	}
}

sub CleanMainbody
{
	my($mainbody_ref)=@_;
	$$mainbody_ref =~ s/\xc2\xa0/\x20/g;
	$$mainbody_ref =~ s/\xe3\x80\x80/\x20/g; # ?τ??
	$$mainbody_ref =~ s/&nbsp;/\x20/igs;
	$$mainbody_ref =~ s/(<p>)|(<p .*?>)/\n/isg;
	$$mainbody_ref =~ s/(<br>)|(<br .*?>)/\n/isg;
	$$mainbody_ref =~ s/<.+?>/\x20/sg;
	$$mainbody_ref =~ s/^\s+//;
	$$mainbody_ref =~ s/\s+$//;
	$$mainbody_ref =~ s/[\x20\x09\x0d]+/\x20/gs;
	$$mainbody_ref =~ s/\x20\n+/\n/gs;
	$$mainbody_ref =~ s/\n+\x20/\n/gs;
	$$mainbody_ref =~ s/\n+/\n\t/gs;
	$$mainbody_ref =~ s/^/\t/gs;
	$$mainbody_ref =~ s/&ndash;//gs;
	$$mainbody_ref =~ s/&trade;//gs;
	$$mainbody_ref =~ s/&ldquo;//gs;
	$$mainbody_ref =~ s/&rdquo;//gs;
	$$mainbody_ref =~ s/&mdash;//gs;
}

sub DeleteDownloadedUrl
{
	my($filename_urllog,$suburl_hash)=@_;
	unless(-e $filename_urllog)
	{
		print "the log file:$filename_urllog does not exists time!\n";
		return;
	}
	if(open(FR,"$filename_urllog"))
	{
		while(<FR>)
		{
			chomp;
			$_=~s/\s+$//;
			if(exists $$suburl_hash{$_})
			{	delete $$suburl_hash{$_};	}
		}
	}
	else
	{	print "could not open the file:$filename_urllog to read!\n";}
	my $really_download=keys %$suburl_hash;
	print "$really_download urls will be really downloaded!\n";
}

sub GetSubUrl
{
	my($today,$filepath_basepage,$channel_en,$baseurl,$suburl_hash)=@_;
	$filepath_basepage=$filepath_basepage."/".$channel_en;
	system "mkdir -p $filepath_basepage";
	my $turnpagecnt=2;
	for(my $i=1;$i<=$turnpagecnt;$i++)
	{
		$baseurl=~s/\.html$/$i\.html/;
		my $filename_basepage=$filepath_basepage."/basepage_".$today."_".$i.".html";
		unless(-e $filename_basepage)
		{
			`wget \"$baseurl\" -O \"$filename_basepage\" -t 1 --timeout=30 --header=$ua_header`;
		}
		my $size=-s $filename_basepage;
		if((1000>$size)||(1_000_000<$size))
		{
			unlink($filename_basepage);
			next;
		}
		if(open(FR,"$filename_basepage"))
		{
			my $str;
			while(<FR>)
			{
				$str.=$_;
			}
			close(FR);
			from_to($str,"gb2312","utf8");
			#while($str=~m/<td style="line-height:24px;"><a href="\s*(.*?)\s*" class="blue5" target="_blank">\s*.*?\s*<\/a>\s*<\/td>\s*<td align="right" class="gray1">\s*(.*?)\s*<\/td>/igs)
			while($str=~m/<td style="line-height:24px;"><a href="(.*?)" class="blue5" target="_blank">\s*.*?\s*<\/a>\s*<\/td>/isg)
			{
				my $url=$1;
				my $date;
				my $str_tmp=$1;
			#	print "$1\n";
				if($str_tmp=~m/\/item\/(.*?)\/\d+\.html/isg)
				{	
			#		print "$1\n";
					$date=$1;
				}
				#print "$1\n$2\n";
				$url="http://news.chemnet.com".$url;
#				print "$date\n$local_time\n";
				if($date eq $today)
				{
					print "############$1\n$url\n";
					$$suburl_hash{$url}++;
				}
			}
			unlink($filename_basepage);
		}
		else
		{	print "could not open the file:$filename_basepage to read!\n";}
		
	}
	my $baseurl_cnt=keys %$suburl_hash;
	print "$baseurl_cnt urls will be downloaded!\n";
}
#die("hahaha\n");
sub ReadConfig
{
	print "reading config file...\n";
	
	my($filename_conf,$baseurl_hash)=@_;
	die("does not exists the config file:$filename_conf ,please check it!\n")unless(-e $filename_conf);
	my($path_out,$dbname,$tbname,$dbuser,$dbpwd,$save);
	my $str;
	open(FR,"$filename_conf")or die("could not open the config file:$filename_conf to read!\n");
	while($str=<FR>)
	{
		chomp($str);
		if($str=~m/^the output dir:\s*'(.+?)'\s*$/igs)
		{	
			$path_out=$1;
			$path_out=~s/\/+$//;
		}
		if($str=~m/^dbname:\s*'(.+?)'\s*$/igs)
		{	$dbname=$1;}
		if($str=~m/^tbname:\s*'(.+?)'\s*$/igs)
		{	$tbname=$1;}
		if($str=~m/^dbuser:\s*'(.+?)'\s*$/igs)
		{	$dbuser=$1;}
		if($str=~m/^dbpwd:\s*'(.+?)'\s*$/igs)
		{	$dbpwd=$1;}
		if($str=~m/^save in disk:\s*'(.+?)'\s*$/igs)
		{
			$save=$1;
			die "Do you want to save the web pages in disk? Plead modify the config file\n" unless($save =~ m/^yes$/i || $save =~ m/^no$/i);
		}
		if($str=~m/^channel:\s*'(.+?)'\s*:\s*'(.+?)'\s*:\s*'(.+?)'\s*$/igs)
		{
			$$baseurl_hash{$2}{0}=$1;
			$$baseurl_hash{$2}{1}=$3;
		}
	}
	die("'path_out'undefined!\n")unless(defined $path_out);
	die("'dbname'undefined!\n")unless(defined $dbname);
	die("'tbname'undefined!\n")unless(defined $tbname);
	die("'dbuser'undefined!\n")unless(defined $dbuser);
	die("'dbpwd'undefined!\n")unless(defined $dbpwd);
	die("'save'undefined!\n")unless(defined $save);
	my $baseurl_cnt=keys %$baseurl_hash;
	die("NO baseurls need to be downloaded!\n")if(0==$baseurl_cnt);
	
	return($path_out,$dbname,$tbname,$dbuser,$dbpwd,$save);
}














